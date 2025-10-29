from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Prefetch, Q
from wagtail.images.models import Rendition
from itertools import chain

# Adjust these imports to your project
from core.models import ContentPage  # or wherever ContentPage lives

DEFAULT_FILTER_SPECS = ["fill-142x80", "fill-2560x1600"]


class Command(BaseCommand):
    help = "Pre-generate Wagtail image renditions used by the Annual Report timeline API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            help="Annual Report year (generates items from Aug 1 of previous year to Jul 31 of this year).",
        )
        parser.add_argument(
            "--start",
            type=str,
            help="Override start date (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--end",
            type=str,
            help="Override end date (YYYY-MM-DD).",
        )
        parser.add_argument(
            "--filter-spec",
            action="append",
            dest="filter_specs",
            default=[],
            help="Rendition filter spec to generate (may be passed multiple times). Defaults to fill-142x80 and fill-2560x1600.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of pages processed (for testing).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List targets but do not generate renditions.",
        )

    def handle(self, *args, **opts):
        year = opts.get("year")
        start = opts.get("start")
        end = opts.get("end")
        limit = opts.get("limit") or 0
        dry_run = opts.get("dry_run")
        filter_specs = opts.get("filter_specs") or DEFAULT_FILTER_SPECS

        if not year and not (start and end):
            raise CommandError("Provide --year or both --start and --end.")

        if year:
            # Aug 1 (year-1) to Jul 31 (year)
            start_date = date(year - 1, 8, 1)
            end_date = date(year, 7, 31)
        else:
            try:
                y1, m1, d1 = [int(x) for x in start.split("-")]
                y2, m2, d2 = [int(x) for x in end.split("-")]
                start_date = date(y1, m1, d1)
                end_date = date(y2, m2, d2)
            except Exception:
                raise CommandError("Invalid --start/--end format. Use YYYY-MM-DD.")

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"Warm renditions from {start_date.isoformat()} to {end_date.isoformat()} "
                f"for filter_specs={filter_specs}"
            )
        )

        # Match the API’s filtering logic closely
        base_qs = (
            ContentPage.objects.live()
            .filter(
                projectpage=None,
                publicationseriespage=None,
                multimediaseriespage=None,
                twentiethpagesingleton=None,
                multimediapage=None,
                articleseriespage=None,
                publishing_date__range=[start_date, end_date],
            )
            .exclude(articlepage__article_type__title__in=["CIGI in the News", "News Releases", "Op-Eds"])
        )

        if limit > 0:
            base_qs = base_qs[:limit]

        total_pages = base_qs.count()
        self.stdout.write(self.style.HTTP_INFO(f"Pages to scan: {total_pages}"))

        pages_iter = base_qs.iterator(chunk_size=200)

        # Stats
        images_seen = 0
        renditions_created = 0
        renditions_existing = 0
        pages_processed = 0

        def generate(img):
            nonlocal renditions_created, renditions_existing, images_seen
            if not img:
                return
            images_seen += 1
            for fs in filter_specs:
                # get_rendition() is idempotent: it reuses existing or creates if missing.
                if dry_run:
                    # Check existence without creating
                    exists = Rendition.objects.filter(image=img, filter_spec=fs).exists()
                    if exists:
                        renditions_existing += 1
                    else:
                        # would create
                        pass
                else:
                    rendition = img.get_rendition(fs)  # may create
                    # We can't easily distinguish created vs existing without an extra check.
                    # Do a cheap check:
                    existed = Rendition.objects.filter(image=img, filter_spec=fs, file=rendition.file.name).exists()
                    if existed:
                        renditions_existing += 1
                    else:
                        renditions_created += 1

        for page in pages_iter:
            sp = page.specific
            # Choose the same image fields your API uses:
            image_candidates = []

            if page.contenttype == "Event":
                image_candidates.append(getattr(sp, "image_hero", None))
            elif page.contenttype == "Opinion":
                image_candidates.append(getattr(sp, "image_hero", None))
            elif page.contenttype == "Publication":
                image_candidates.append(getattr(sp, "image_feature", None))
            else:
                # If some types might use either, include both safely
                image_candidates.extend([
                    getattr(sp, "image_hero", None),
                    getattr(sp, "image_feature", None),
                ])

            # De-dup in case the same image is referenced twice
            unique_images = [img for img in {id(i): i for i in image_candidates if i}.values()]

            for img in unique_images:
                generate(img)

            pages_processed += 1
            if pages_processed % 100 == 0:
                self.stdout.write(f"Processed {pages_processed}/{total_pages} pages…")

        self.stdout.write(self.style.SUCCESS("Done."))
        self.stdout.write(
            self.style.HTTP_INFO(
                f"Pages processed: {pages_processed}\n"
                f"Images seen: {images_seen}\n"
                f"Renditions existing (counted): {renditions_existing}\n"
                f"Renditions created (approx): {renditions_created}"
            )
        )
