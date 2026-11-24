"""Export recently published Wagtail pages as a reviewable content overlay."""

import calendar
import hashlib
import json
from pathlib import Path, PurePosixPath

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from modelcluster.models import get_all_child_relations
from wagtail.models import Page, ReferenceIndex, Site


SCHEMA = "cigionline.content-overlay/v1"
FILE_MODELS = {
    "images.cigionlineimage": "file",
    "wagtaildocs.document": "file",
    "wagtailmedia.media": "file",
}
OMIT_PAGE_COLUMNS = {"owner_id", "locked_by_id"}


def subtract_months(value, months):
    month = value.month - months - 1
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def fetch_row(table, column, value):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM {connection.ops.quote_name(table)} "
            f"WHERE {connection.ops.quote_name(column)} = %s",
            [value],
        )
        columns = [description.name for description in cursor.description]
        row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def fetch_rows(table, column, value, order_by=()):
    order = ""
    if order_by:
        order = " ORDER BY " + ", ".join(connection.ops.quote_name(name) for name in order_by)
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM {connection.ops.quote_name(table)} "
            f"WHERE {connection.ops.quote_name(column)} = %s{order}",
            [value],
        )
        columns = [description.name for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def table_columns(table):
    with connection.cursor() as cursor:
        return {column.name for column in connection.introspection.get_table_description(cursor, table)}


def model_rows(model, source_pk):
    rows = {}
    seen = set()
    for parent in [*reversed(model._meta.get_parent_list()), model]:
        table = parent._meta.db_table
        if table in seen:
            continue
        seen.add(table)
        row = fetch_row(table, parent._meta.pk.column, source_pk)
        if row is not None:
            if parent is Page:
                for name in OMIT_PAGE_COLUMNS:
                    row.pop(name, None)
            rows[table] = row
    return rows


def specific_page_data(source_pk):
    page_row = fetch_row(Page._meta.db_table, Page._meta.pk.column, source_pk)
    if page_row is None:
        raise CommandError(f"Referenced page {source_pk} does not exist")
    content_type = ContentType.objects.get_for_id(page_row["content_type_id"])
    model = content_type.model_class()
    if model is None:
        raise CommandError(f"Page {source_pk} uses unavailable model {content_type.app_label}.{content_type.model}")
    return model, page_row, model_rows(model, source_pk)


def page_key(model, page_row, rows):
    # url_path is stable across environments; parent path + slug is the approved fallback key.
    parent_url_path = page_row["url_path"].removesuffix(f"{page_row['slug']}/")
    key = {
        "model": model._meta.label_lower,
        "parent_url_path": parent_url_path,
        "slug": page_row["slug"],
    }
    for row in rows.values():
        if row.get("drupal_node_id") is not None:
            key["drupal_node_id"] = row["drupal_node_id"]
            break
    return key


def object_data(model, source_pk):
    if issubclass(model, Page):
        specific_model, page_row, rows = specific_page_data(source_pk)
        return specific_model, page_key(specific_model, page_row, rows), rows

    row = fetch_row(model._meta.db_table, model._meta.pk.column, source_pk)
    if row is None:
        raise CommandError(f"Referenced {model._meta.label_lower} {source_pk} does not exist")
    label = model._meta.label_lower
    key = {"model": label}
    if label in FILE_MODELS:
        key.update(
            file=row.get(FILE_MODELS[label]),
            wagtail_file_hash=row.get("file_hash"),
            title=row.get("title", ""),
        )
    else:
        for name in ("drupal_node_id", "drupal_taxonomy_id", "slug", "name", "title", "key"):
            if row.get(name) not in (None, ""):
                key[name] = row[name]
    return model, key, {model._meta.db_table: row}


def add_dependency(model, source_pk, dependencies):
    model, stable_key, rows = object_data(model, source_pk)
    dependency_id = f"{model._meta.label_lower}:{source_pk}"
    dependencies.setdefault(
        dependency_id,
        {"source_pk": str(source_pk), "stable_key": stable_key, "rows": rows},
    )
    return dependency_id


def reference_rows(source_pk, model, dependencies):
    page_content_type = ContentType.objects.get_for_model(Page, for_concrete_model=False)
    rows = []
    references = ReferenceIndex.objects.filter(
        base_content_type=page_content_type,
        object_id=str(source_pk),
    ).select_related("to_content_type")
    for reference in references.iterator():
        target_model = reference.to_content_type.model_class()
        dependency_id = add_dependency(target_model, reference.to_object_id, dependencies)
        rows.append(
            {
                "model_path": reference.model_path,
                "content_path": reference.content_path,
                "dependency": dependency_id,
            }
        )

    for field in model._meta.many_to_many:
        if field.auto_created:
            continue
        through = field.remote_field.through
        source_column = field.m2m_column_name()
        target_column = field.m2m_reverse_name()
        if source_column not in table_columns(through._meta.db_table):
            continue
        for relation in fetch_rows(through._meta.db_table, source_column, source_pk):
            target_pk = relation[target_column]
            dependency_id = add_dependency(field.related_model, target_pk, dependencies)
            rows.append(
                {
                    "model_path": field.name,
                    "content_path": field.name,
                    "dependency": dependency_id,
                }
            )
    return sorted(rows, key=lambda row: (row["content_path"], row["dependency"]))


def child_rows(model, source_pk):
    children = {}
    for relation in get_all_child_relations(model):
        child_model = relation.related_model
        table = child_model._meta.db_table
        columns = table_columns(table)
        order = [name for name in ("sort_order", child_model._meta.pk.column) if name in columns]
        rows = fetch_rows(table, relation.field.column, source_pk, order)
        for row in rows:
            row.pop(relation.field.column, None)
        if rows:
            children[relation.get_accessor_name()] = {"model": child_model._meta.label_lower, "rows": rows}
    return children


def many_to_many_rows(model, source_pk):
    relations = {}
    for field in model._meta.many_to_many:
        if field.auto_created:
            continue
        through = field.remote_field.through
        source_column = field.m2m_column_name()
        columns = table_columns(through._meta.db_table)
        if source_column not in columns:
            continue
        rows = fetch_rows(through._meta.db_table, source_column, source_pk)
        for row in rows:
            row.pop(source_column, None)
        if rows:
            relations[field.name] = {"model": through._meta.label_lower, "rows": rows}
    return relations


def copy_files(dependencies, output_dir):
    files = []
    for dependency_id, dependency in sorted(dependencies.items()):
        label = dependency["stable_key"]["model"]
        field_name = FILE_MODELS.get(label)
        if field_name is None:
            continue
        model = apps.get_model(label)
        obj = model._base_manager.get(pk=dependency["source_pk"])
        source = getattr(obj, field_name)
        relative = PurePosixPath(source.name)
        if relative.is_absolute() or ".." in relative.parts:
            raise CommandError(f"Unsafe storage path: {source.name}")
        destination = output_dir / "files" / Path(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        size = 0
        with source.open("rb") as source_file, destination.open("wb") as output_file:
            while chunk := source_file.read(1024 * 1024):
                output_file.write(chunk)
                digest.update(chunk)
                size += len(chunk)
        files.append(
            {
                "dependency": dependency_id,
                "storage_name": source.name,
                "bundle_path": destination.relative_to(output_dir).as_posix(),
                "size": size,
                "sha256": digest.hexdigest(),
            }
        )
    return files


class Command(BaseCommand):
    help = "Export live pages published since a date (default: three months ago)."

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True, help="Output JSON manifest path.")
        parser.add_argument("--since", help="Inclusive ISO-8601 publication timestamp.")
        parser.add_argument("--months", type=int, default=3, help="Months before now (default: 3).")
        parser.add_argument(
            "--include-files",
            action="store_true",
            help="Copy referenced image, document, and media originals beside the manifest.",
        )

    def handle(self, *args, **options):
        if options["months"] < 1:
            raise CommandError("--months must be at least 1")
        now = timezone.now()
        cutoff = parse_datetime(options["since"]) if options["since"] else subtract_months(now, options["months"])
        if cutoff is None:
            raise CommandError("--since must be a valid ISO-8601 timestamp")
        if timezone.is_naive(cutoff):
            cutoff = timezone.make_aware(cutoff)

        pages = list(Page.objects.live().filter(last_published_at__gte=cutoff).order_by("last_published_at", "pk"))
        sites = [
            {"hostname": site.hostname, "port": site.port, "root_url_path": site.root_page.url_path}
            for site in Site.objects.select_related("root_page").order_by("hostname", "port")
        ]
        dependencies = {}
        exported_pages = []
        for page in pages:
            model = page.content_type.model_class()
            rows = model_rows(model, page.pk)
            exported_pages.append(
                {
                    "source_pk": str(page.pk),
                    "stable_key": page_key(model, rows[Page._meta.db_table], rows),
                    "title": page.title,
                    "url_path": page.url_path,
                    "full_url": page.full_url,
                    "locale": page.locale.language_code,
                    "published_at": page.last_published_at.isoformat(),
                    "model_rows": rows,
                    "child_relations": child_rows(model, page.pk),
                    "many_to_many": many_to_many_rows(model, page.pk),
                    "references": reference_rows(page.pk, model, dependencies),
                }
            )

        output = Path(options["output"]).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        files = copy_files(dependencies, output.parent) if options["include_files"] else []
        artifact = {
            "schema": SCHEMA,
            "generated_at": now.isoformat(),
            "selection": {"live": True, "last_published_at_gte": cutoff.isoformat()},
            "sites": sites,
            "counts": {
                "pages": len(exported_pages),
                "dependencies": len(dependencies),
                "files": len(files),
            },
            "pages": exported_pages,
            "dependencies": dependencies,
            "files": files,
        }
        output.write_text(
            json.dumps(artifact, indent=2, sort_keys=True, cls=DjangoJSONEncoder) + "\n"
        )
        checked = json.loads(output.read_text())
        if checked["counts"]["pages"] != len(pages):
            raise CommandError("Export verification failed: page count changed")
        self.stdout.write(
            self.style.SUCCESS(
                f"Exported {len(exported_pages)} pages, {len(dependencies)} dependencies, "
                f"and {len(files)} files to {output}"
            )
        )
