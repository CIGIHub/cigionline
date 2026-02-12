from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from events.models import EmailCampaign, Registrant
from events.emailing import send_event_campaign_email


class Command(BaseCommand):
    help = (
        "Send due EmailCampaign messages for event registrations (reminders / waitlist notices). "
        "Idempotent via per-registrant send records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--due-before",
            dest="due_before",
            default=None,
            help="ISO datetime; only send campaigns scheduled up to this instant (defaults to now).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Compute recipients but don't send emails.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Max recipient sends per run (default: 500).",
        )

    def handle(self, *args, **opts):
        due_before = opts["due_before"]
        dry_run = opts["dry_run"]
        limit = opts["limit"]

        cutoff = timezone.now()
        if due_before:
            cutoff = timezone.datetime.fromisoformat(due_before)
            if timezone.is_naive(cutoff):
                cutoff = timezone.make_aware(cutoff, timezone.get_current_timezone())

        campaigns = (
            EmailCampaign.objects.select_related("event", "template")
            .filter(scheduled_for__lte=cutoff)
            .order_by("scheduled_for", "id")
        )

        total_sends = 0
        for camp in campaigns:
            if camp.completed_at:
                continue

            statuses = camp.get_include_statuses()
            type_slugs = camp.get_include_type_slugs()

            qs = Registrant.objects.filter(event=camp.event)
            if statuses:
                qs = qs.filter(status__in=statuses)
            if type_slugs:
                qs = qs.filter(registration_type__slug__in=type_slugs)

            # Skip cancelled always
            qs = qs.exclude(status=Registrant.Status.CANCELLED)

            # Only send to unsent recipients (idempotent)
            qs = qs.exclude(campaign_sends__campaign=camp)

            remaining_for_campaign = 0

            for registrant in qs.order_by("id")[: max(0, limit - total_sends)]:
                if total_sends >= limit:
                    break

                if not camp.sent_at and not dry_run:
                    camp.sent_at = timezone.now()
                    camp.save(update_fields=["sent_at"])

                if dry_run:
                    self.stdout.write(
                        f"[dry-run] would send campaign={camp.id} to registrant={registrant.id} ({registrant.email})"
                    )
                else:
                    # record send + send email
                    with transaction.atomic():
                        send_event_campaign_email(camp, registrant)

                total_sends += 1

            # If there are no remaining unsent recipients, mark campaign complete.
            if total_sends < limit:
                remaining_ids = list(qs.order_by("id").values_list("id", flat=True)[:1])
                if len(remaining_ids) == 0 and not dry_run and not camp.completed_at:
                    camp.completed_at = timezone.now()
                    camp.save(update_fields=["completed_at"])

            if total_sends >= limit:
                break

        self.stdout.write(self.style.SUCCESS(f"Done. Sends: {total_sends}"))
