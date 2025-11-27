from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from wagtail.models import PageLogEntry

from events.models import EventPage


class Command(BaseCommand):
    help = (
        "Re-publish EventPage instances recently unpublished by Hillary Weaver, "
        "if exclude_from_search is False."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--months",
            type=int,
            default=1,
            help="How many months back to look for recent unpublishes (default: 1).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without publishing.",
        )

    def handle(self, *args, **options):
        months = options["months"]
        dry_run = options["dry_run"]

        cutoff = timezone.now() - relativedelta(months=months)

        User = get_user_model()

        try:
            hillary = User.objects.get(first_name="Hilary", last_name="Weaver")
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR("Could not find user 'Hilary Weaver'."))
            return
        except User.MultipleObjectsReturned:
            self.stderr.write(
                self.style.ERROR(
                    "Multiple users named 'Jonathan Xu' found – refine the lookup."
                )
            )
            return

        self.stdout.write(
            f"Looking for EventPages unpublished by {hillary} "
            f"in the last {months} month(s). Cutoff: {cutoff.isoformat()}"
        )

        event_qs = EventPage.objects.filter(live=False)

        processed = 0
        republished = 0

        for event in event_qs:
            processed += 1

            # Only process pages whose latest revision is after 2016
            latest_rev = event.get_latest_revision()
            if not latest_rev:
                self.stdout.write(
                    f"Skipping {event.title} (id={event.id}) – no revisions found."
                )
                continue

            rev_date = getattr(latest_rev, "created_at", None) or getattr(
                latest_rev, "submitted_at", None
            )

            if not rev_date:
                self.stdout.write(
                    f"Skipping {event.title} (id={event.id}) – latest revision has no timestamp."
                )
                continue

            if rev_date.year <= 2016:
                self.stdout.write(
                    f"Skipping {event.title} (id={event.id}) – latest revision is from {rev_date.year}."
                )
                continue

            last_unpublish = (
                PageLogEntry.objects.filter(
                    page=event,
                    action="wagtail.unpublish",
                    user=hillary,
                    timestamp__gte=cutoff,
                )
                .order_by("-timestamp")
                .first()
            )

            if not last_unpublish:
                continue

            if event.exclude_from_search:
                self.stdout.write(
                    f"Skipping {event.title} (id={event.id}) – exclude_from_search=True."
                )
                continue

            old_value = event.exclude_from_search
            new_value = True

            action_text = "Would update & publish" if dry_run else "Updating & publishing"
            self.stdout.write(
                f"{action_text} {event.title} (id={event.id}); "
                f"unpublished at {last_unpublish.timestamp}. "
                f"latest revision year={rev_date.year}. "
                f"exclude_from_search: {old_value} -> {new_value}"
            )

            if not dry_run:
                event.exclude_from_search = True
                revision = event.save_revision(user=hillary)
                revision.publish(user=hillary)
                republished += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Processed {processed} EventPages; republished {republished}."
            )
        )
