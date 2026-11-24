"""Import an allow-listed page overlay exported by export_recent_pages."""

import copy
import hashlib
import json
import re
from pathlib import Path
from types import SimpleNamespace

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import models, transaction
from modelcluster.models import get_all_child_relations
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.models import Collection

from .export_recent_pages import SCHEMA


DEFAULT_MODELS = {
    "core.basicpage",
    "home.homepage",
    "multimedia.multimediapage",
    "research.projectpage",
    "research.themepage",
    "subscribe.subscribepage",
}
PAGE_FIELDS = {"title", "draft_title", "seo_title", "search_description", "show_in_menus"}
PROJECT_TARGET_TITLES = {
    "AI for Governance": ("AI for Governance", "AI Empowerment for a Prosperous Future"),
    "Global AI Risks": ("Global AI Risks", "Global AI Risks Initiative"),
    "Space Governance": ("Space Governance", "Space Governance 4.0"),
    "National Security and Cybersecurity": (
        "National Security and Cybersecurity",
        "Strengthening Canada’s National Security in a Complex World",
    ),
    "Freedom of Thought": ("Freedom of Thought", "Legitimate Influence or Unlawful Manipulation?"),
    "Governance of Digital Money and Assets": (
        "Governance of Digital Money and Assets",
        "Digital Assets in a Deglobalized World",
    ),
    "Next-Generation Economies": (
        "Next-Generation Economies",
        "Next-Generation Economies: Middle Powers in a Changing World",
    ),
    "Canada-U.S. Relations in the Second Century": (
        "Canada-U.S. Relations in the Second Century",
        "Canada-US Relations in the Second Century",
    ),
}
SUPERSEDED_PROJECT_TITLES = {
    title
    for source_title, titles in PROJECT_TARGET_TITLES.items()
    for title in titles
    if title != source_title
}
PRESERVED_MANY_TO_MANY = {"research.projectpage": {"topics"}}


def page_title(entry):
    return entry["model_rows"]["wagtailcore_page"]["title"]


def resolve_page(entry):
    key = entry["stable_key"]
    model = apps.get_model(key["model"])
    if key.get("drupal_node_id") is not None and hasattr(model, "drupal_node_id"):
        matches = model.objects.filter(drupal_node_id=key["drupal_node_id"])
    else:
        matches = model.objects.filter(url_path=entry["url_path"])

    if not matches.exists() and key["model"] == "research.projectpage":
        titles = PROJECT_TARGET_TITLES.get(page_title(entry), (page_title(entry),))
        matches = model.objects.filter(title__in=titles)

    found = list(matches.order_by("pk")[:2])
    if len(found) > 1:
        path_matches = [page for page in found if page.url_path == entry["url_path"]]
        if len(path_matches) == 1:
            return path_matches[0]
    if len(found) != 1:
        raise CommandError(
            f"{entry['title']!r} ({entry['url_path']}): expected one target {key['model']}, "
            f"found {len(found)}"
        )
    return found[0]


def dependency_title(dependency):
    page_row = dependency["rows"].get("wagtailcore_page")
    return page_row.get("title") if page_row else None


def resolve_dependency(
    dependency,
    create_missing_assets=False,
    create_missing_pages=False,
    pending_pages=None,
):
    key = dependency["stable_key"]
    model = apps.get_model(key["model"])
    if issubclass(model, Page):
        entry = {
            "source_pk": str(dependency["source_pk"]),
            "stable_key": key,
            "url_path": dependency["rows"]["wagtailcore_page"]["url_path"],
            "title": dependency_title(dependency),
            "model_rows": dependency["rows"],
        }
        identity = (key["model"], entry["url_path"])
        if pending_pages is not None and identity in pending_pages:
            return pending_pages[identity]
        try:
            return resolve_page(entry)
        except CommandError:
            title_matches = list(model.objects.filter(title=entry["title"]).order_by("pk")[:2])
            if len(title_matches) == 1:
                return title_matches[0]
            if create_missing_pages and key["model"] == "core.basicpage":
                pending = PendingPage(model, entry)
                pending_pages[identity] = pending
                return pending
            raise

    if "file" in key:
        if key.get("wagtail_file_hash") and hasattr(model, "file_hash"):
            matches = model._base_manager.filter(file_hash=key["wagtail_file_hash"])
            if matches.count() > 1:
                matches = matches.filter(file=key["file"])
                if matches.count() > 1:
                    return matches.order_by("pk").first()
            if not matches.exists() and model._base_manager.filter(file=key["file"]).exists():
                raise CommandError(f"asset filename exists with different bytes: {key['file']}")
        else:
            matches = model._base_manager.filter(file=key["file"])
        if not matches.exists() and create_missing_assets:
            return PendingAsset(model, dependency)
    else:
        filters = {
            name: key[name]
            for name in ("drupal_node_id", "drupal_taxonomy_id", "slug", "name", "title", "key")
            if key.get(name) not in (None, "") and hasattr(model, name)
        }
        if not filters:
            raise CommandError(f"{key['model']}:{dependency['source_pk']} has no stable target key")
        matches = model._base_manager.filter(**filters)

    found = list(matches.order_by("pk")[:2])
    if len(found) != 1:
        raise CommandError(
            f"dependency {key} (source {dependency['source_pk']}): expected one target, found {len(found)}"
        )
    return found[0]


class PendingAsset(SimpleNamespace):
    def __init__(self, model, dependency):
        super().__init__(model=model, dependency=dependency, pk=int(dependency["source_pk"]))

    def create(self):
        row = self.dependency["rows"][self.model._meta.db_table]
        values = {}
        for field in self.model._meta.concrete_fields:
            if field.primary_key or field.name == "uploaded_by_user":
                continue
            if field.name == "collection":
                values[field.attname] = Collection.get_first_root_node().pk
                continue
            if field.column in row:
                values[field.attname if field.is_relation else field.name] = row[field.column]
        return self.model._base_manager.create(**values)


class PendingPage(SimpleNamespace):
    def __init__(self, model, entry):
        super().__init__(
            model=model,
            entry=entry,
            pk=-int(entry["source_pk"]),
            title=entry["title"],
            url_path=entry["url_path"],
            created=None,
        )

    def validate(self, pending_pages):
        parent_path = self.entry["stable_key"]["parent_url_path"]
        if not any(path == parent_path for _, path in pending_pages):
            parents = list(Page.objects.filter(url_path=parent_path)[:2])
            if len(parents) != 1:
                raise CommandError(
                    f"{self.entry['title']!r}: expected one parent at {parent_path!r}, "
                    f"found {len(parents)}"
                )
        conflicts = list(Page.objects.filter(url_path=self.entry["url_path"])[:2])
        if len(conflicts) > 1:
            raise CommandError(
                f"{self.entry['title']!r}: multiple pages already use {self.entry['url_path']!r}"
            )
        if conflicts and conflicts[0].numchild:
            raise CommandError(
                f"Cannot move conflicting page {conflicts[0].title!r}: it has child pages"
            )

    def create(self, pending_pages, user):
        if self.created is not None:
            return self.created

        parent_path = self.entry["stable_key"]["parent_url_path"]
        parent_pending = next(
            (pending for (_, path), pending in pending_pages.items() if path == parent_path),
            None,
        )
        if parent_pending is not None:
            parent = parent_pending.create(pending_pages, user)
        else:
            parents = list(Page.objects.filter(url_path=parent_path).order_by("pk")[:2])
            if len(parents) != 1:
                raise CommandError(
                    f"{self.entry['title']!r}: expected one parent at {parent_path!r}, "
                    f"found {len(parents)}"
                )
            parent = parents[0]

        conflicts = list(Page.objects.filter(url_path=self.entry["url_path"]).order_by("pk")[:2])
        if len(conflicts) > 1:
            raise CommandError(
                f"{self.entry['title']!r}: multiple pages already use {self.entry['url_path']!r}"
            )
        if conflicts:
            move_to_legacy_path(conflicts[0], parent, user)

        page = self.model(
            title=self.entry["title"],
            draft_title=self.entry["title"],
            slug=self.entry["stable_key"]["slug"],
            live=False,
            has_unpublished_changes=True,
        )
        parent.add_child(instance=page)
        page.save_revision(user=user, log_action=True)
        self.created = page
        return page


def move_to_legacy_path(page, parent, user):
    if page.numchild:
        raise CommandError(f"Cannot move conflicting page {page.title!r}: it has child pages")
    base_slug = f"{page.slug}-legacy"
    slug = base_slug
    suffix = 2
    while parent.get_children().filter(slug=slug).exclude(pk=page.pk).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    specific = page.specific
    if type(specific) is Page:
        Page.objects.filter(pk=page.pk).update(
            slug=slug,
            url_path=f"{parent.url_path}{slug}/",
        )
    else:
        specific.slug = slug
        specific.save_revision(user=user, log_action=True).publish()


def set_json_reference(value, path, target_pk):
    tokens = path.split(".")
    current = value
    for index, token in enumerate(tokens):
        last = index == len(tokens) - 1
        if isinstance(current, list):
            item = next(
                (item for item in current if isinstance(item, dict) and str(item.get("id")) == token),
                None,
            )
            if item is not None:
                if last:
                    item["value"] = target_pk
                    return
                current = item["value"]
                continue
            if token.isdigit() and int(token) < len(current):
                if last:
                    current[int(token)] = target_pk
                    return
                current = current[int(token)]
                continue
            raise CommandError(f"Cannot find list item {token!r} in reference path {path!r}")
        if isinstance(current, dict) and token in current:
            if last:
                current[token] = target_pk
                return
            current = current[token]
            continue
        raise CommandError(f"Cannot find {token!r} in reference path {path!r}")
    raise CommandError(f"Empty reference path {path!r}")


def replace_rich_text_reference(value, source_pk, target_pk):
    pattern = re.compile(rf"(\bid\s*=\s*['\"]){re.escape(str(source_pk))}(['\"])")
    replaced, count = pattern.subn(rf"\g<1>{target_pk}\2", value)
    if count == 0:
        raise CommandError(f"Could not find rich-text reference id={source_pk}")
    return replaced


def find_model_row(entry, column):
    matches = [row for row in entry["model_rows"].values() if column in row]
    if len(matches) != 1:
        raise CommandError(f"Expected one source column {column!r} on {entry['title']!r}, found {len(matches)}")
    return matches[0]


def remap_references(entry, resolved_dependencies):
    for reference in entry["references"]:
        if reference["model_path"] in PRESERVED_MANY_TO_MANY.get(entry["stable_key"]["model"], set()):
            continue
        dependency = reference["dependency"]
        target_pk = resolved_dependencies[dependency].pk
        source_pk = entry["_dependencies"][dependency]["source_pk"]
        parts = reference["content_path"].split(".")
        field_name = parts[0]

        child = entry["child_relations"].get(field_name)
        if child is not None:
            source_child_pk, child_field_name = parts[1], parts[-1]
            row = next((row for row in child["rows"] if str(row.get("id")) == source_child_pk), None)
            if row is None:
                raise CommandError(f"Missing child {field_name}.{source_child_pk}")
            child_model = apps.get_model(child["model"])
            field = child_model._meta.get_field(child_field_name)
            row[field.column] = target_pk
            continue

        model = apps.get_model(entry["stable_key"]["model"])
        field = model._meta.get_field(field_name)
        if field.many_to_many:
            continue
        row = find_model_row(entry, field.column)
        raw = row[field.column]
        if isinstance(field, StreamField):
            data = json.loads(raw) if isinstance(raw, str) else raw
            set_json_reference(data, ".".join(parts[1:]), target_pk)
            row[field.column] = data
        elif hasattr(field, "extract_references") and isinstance(raw, str):
            row[field.column] = replace_rich_text_reference(raw, source_pk, target_pk)
        elif field.is_relation and field.many_to_one:
            row[field.column] = target_pk
        else:
            raise CommandError(f"Unsupported reference field {model._meta.label}.{field_name}")


def assign_page_fields(target, entry):
    changed = []
    model = type(target)
    label = model._meta.label_lower
    for field in model._meta.concrete_fields:
        if field.primary_key or field.auto_created or getattr(field.remote_field, "parent_link", False):
            continue
        if label == "home.homepage" and field.name != "body":
            continue
        if field.model is Page and field.name not in PAGE_FIELDS:
            continue
        row = next((row for row in entry["model_rows"].values() if field.column in row), None)
        if row is None:
            continue
        value = row[field.column]
        if isinstance(field, StreamField) and isinstance(value, str):
            value = json.loads(value)
        attribute = field.attname if field.is_relation and field.many_to_one else field.name
        if getattr(target, attribute) != value:
            setattr(target, attribute, value)
            changed.append(field.name)
    return changed


def replace_child_relations(target, entry):
    if target._meta.label_lower == "home.homepage":
        return
    relations = {relation.get_accessor_name(): relation for relation in get_all_child_relations(type(target))}
    for name, relation in relations.items():
        source = entry["child_relations"].get(name)
        manager = getattr(target, name)
        manager.all().delete()
        if source is None:
            continue
        child_model = relation.related_model
        for source_row in source["rows"]:
            values = {}
            for field in child_model._meta.concrete_fields:
                if field.primary_key or field == relation.field:
                    continue
                if field.column in source_row:
                    values[field.attname if field.is_relation else field.name] = source_row[field.column]
            child_model._base_manager.create(**{relation.field.attname: target.pk}, **values)


def replace_many_to_many(target, entry, source_to_target):
    if target._meta.label_lower == "home.homepage":
        return
    for field in type(target)._meta.many_to_many:
        if field.auto_created:
            continue
        if field.name in PRESERVED_MANY_TO_MANY.get(target._meta.label_lower, set()):
            continue
        source = entry["many_to_many"].get(field.name)
        if source is None:
            getattr(target, field.name).clear()
            continue
        target_column = field.m2m_reverse_name()
        target_ids = []
        label = field.related_model._meta.label_lower
        for row in source["rows"]:
            key = (label, str(row[target_column]))
            if key not in source_to_target:
                raise CommandError(f"Unresolved many-to-many dependency {key}")
            target_ids.append(source_to_target[key])
        getattr(target, field.name).set(target_ids)


class Command(BaseCommand):
    help = "Import an allow-listed content overlay (dry-run by default)."

    def add_arguments(self, parser):
        parser.add_argument("--artifact", required=True)
        parser.add_argument("--model", action="append", dest="models", help="Page model to import; repeatable.")
        parser.add_argument(
            "--create-missing-assets",
            action="store_true",
            help="Create missing image/document/media metadata using existing storage paths.",
        )
        parser.add_argument(
            "--create-missing-pages",
            action="store_true",
            help="Create missing BasicPages and move conflicting legacy page types aside.",
        )
        parser.add_argument("--user", help="Username recorded on imported Wagtail revisions.")
        parser.add_argument("--apply", action="store_true", help="Publish changes (default: dry-run).")

    def handle(self, *args, **options):
        artifact_path = Path(options["artifact"]).expanduser().resolve()
        artifact = json.loads(artifact_path.read_text())
        if artifact.get("schema") != SCHEMA:
            raise CommandError(f"Unsupported artifact schema: {artifact.get('schema')!r}")
        expected_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        allowed_models = set(options["models"] or DEFAULT_MODELS)
        revision_user = None
        if options["apply"]:
            if not options["user"]:
                raise CommandError("--user is required with --apply")
            users = list(get_user_model().objects.filter(
                username=options["user"],
                is_active=True,
            )[:2])
            if len(users) != 1:
                raise CommandError(
                    f"Expected one active user named {options['user']!r}, found {len(users)}"
                )
            revision_user = users[0]

        selected = []
        skipped = []
        for source in artifact["pages"]:
            if source["stable_key"]["model"] not in allowed_models:
                continue
            if source["stable_key"]["model"] == "research.projectpage" and page_title(source) in SUPERSEDED_PROJECT_TITLES:
                skipped.append(source["title"])
                continue
            selected.append(copy.deepcopy(source))

        errors = []
        page_targets = {}
        target_sources = {}
        pending_pages = {}
        for source in selected:
            try:
                target = resolve_page(source)
            except CommandError as exc:
                if options["create_missing_pages"] and source["stable_key"]["model"] == "core.basicpage":
                    identity = (source["stable_key"]["model"], source["url_path"])
                    target = pending_pages.setdefault(
                        identity,
                        PendingPage(apps.get_model(source["stable_key"]["model"]), source),
                    )
                else:
                    errors.append(str(exc))
                    continue
            if target.pk in target_sources:
                errors.append(
                    f"source collision: {target_sources[target.pk]!r} and {source['title']!r} both map to target {target.pk}"
                )
                continue
            page_targets[source["source_pk"]] = target
            target_sources[target.pk] = source["title"]

        needed = {
            reference["dependency"]
            for source in selected
            for reference in source["references"]
            if reference["model_path"]
            not in PRESERVED_MANY_TO_MANY.get(source["stable_key"]["model"], set())
        }
        resolved_dependencies = {}
        source_to_target = {}
        for dependency_id in sorted(needed):
            dependency = artifact["dependencies"][dependency_id]
            try:
                target = resolve_dependency(
                    dependency,
                    options["create_missing_assets"],
                    options["create_missing_pages"],
                    pending_pages,
                )
            except CommandError as exc:
                errors.append(str(exc))
                continue
            resolved_dependencies[dependency_id] = target
            source_to_target[(dependency["stable_key"]["model"], str(dependency["source_pk"]))] = target.pk

        for pending in pending_pages.values():
            try:
                pending.validate(pending_pages)
            except CommandError as exc:
                errors.append(str(exc))

        for source_pk, target in page_targets.items():
            source_model = next(source["stable_key"]["model"] for source in selected if source["source_pk"] == source_pk)
            source_to_target[(source_model, str(source_pk))] = target.pk

        if errors:
            raise CommandError("Overlay preflight failed:\n- " + "\n- ".join(errors))

        for source in selected:
            validation_source = copy.deepcopy(source)
            validation_source["_dependencies"] = artifact["dependencies"]
            remap_references(validation_source, resolved_dependencies)

        self.stdout.write(f"artifact sha256: {expected_hash}")
        self.stdout.write(f"selected: {len(selected)}; superseded source pages skipped: {len(skipped)}")
        self.stdout.write(
            f"missing asset metadata to create: "
            f"{sum(isinstance(target, PendingAsset) for target in resolved_dependencies.values())}"
        )
        self.stdout.write(f"missing BasicPages to create: {len(pending_pages)}")
        for source in selected:
            target = page_targets[source["source_pk"]]
            self.stdout.write(
                f"update {source['title']} ({source['url_path']}) -> "
                f"{target.title} ({target.url_path}, pk={target.pk})"
            )
        if not options["apply"]:
            self.stdout.write(self.style.WARNING("Dry run — pass --apply to publish changes."))
            return

        with transaction.atomic():
            created_pages = {
                identity: pending.create(pending_pages, revision_user)
                for identity, pending in pending_pages.items()
            }
            for source_pk, target in list(page_targets.items()):
                if isinstance(target, PendingPage):
                    page_targets[source_pk] = created_pages[
                        (target.entry["stable_key"]["model"], target.entry["url_path"])
                    ]
            for dependency_id, target in list(resolved_dependencies.items()):
                if isinstance(target, PendingPage):
                    resolved_dependencies[dependency_id] = created_pages[
                        (target.entry["stable_key"]["model"], target.entry["url_path"])
                    ]
            for dependency_id, target in list(resolved_dependencies.items()):
                if isinstance(target, PendingAsset):
                    resolved_dependencies[dependency_id] = target.create()
            for dependency_id, target in resolved_dependencies.items():
                dependency = artifact["dependencies"][dependency_id]
                source_to_target[(
                    dependency["stable_key"]["model"],
                    str(dependency["source_pk"]),
                )] = target.pk
            for source_pk, target in page_targets.items():
                source_model = next(
                    source["stable_key"]["model"]
                    for source in selected
                    if source["source_pk"] == source_pk
                )
                source_to_target[(source_model, str(source_pk))] = target.pk
            for source in selected:
                source = copy.deepcopy(source)
                source["_dependencies"] = artifact["dependencies"]
                remap_references(source, resolved_dependencies)
                target = page_targets[source["source_pk"]]
                assign_page_fields(target, source)
                replace_child_relations(target, source)
                replace_many_to_many(target, source, source_to_target)
                target.save_revision(user=revision_user, log_action=True).publish()

        self.stdout.write(self.style.SUCCESS(f"Published {len(selected)} page overlays."))
