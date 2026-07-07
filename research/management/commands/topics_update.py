from django.core.management.base import BaseCommand

from research.models import ContentPage, TopicPage


class Command(BaseCommand):
    help = "Update topic tags on all tagged content pages."

    TOPIC_REPLACEMENTS = {
        "Gender": "Human Rights",
        "Digital Rights": "Digital Governance",
        "Global Cooperation": "Geopolitics",
        "G7/G20": "Multilateral Institutions",
        "Foreign Interference": "Democracy",
    }

    TOPICS_TO_UNTAG_ARCHIVE_UNPUBLISH = [
        "Surveillance",
        "Competition",
        "Freedom of Thought",
        "Space Governance",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without saving.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        grand_total_pages = 0
        grand_total_add_and_remove = 0
        grand_total_remove_only = 0

        grand_total_untagged_pages = 0
        grand_total_pages_left_without_topics = 0
        pages_left_without_topics = []

        self.stdout.write("")
        self.stdout.write("Replacing topic tags")

        for former_title, latter_title in self.TOPIC_REPLACEMENTS.items():
            former_topic = TopicPage.objects.filter(title=former_title).first()
            latter_topic = TopicPage.objects.filter(title=latter_title).first()

            self.stdout.write("")
            self.stdout.write(f'"{former_title}" -> "{latter_title}"')

            if not former_topic:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping: former topic not found: "{former_title}"'
                    )
                )
                continue

            if not latter_topic:
                self.stdout.write(
                    self.style.WARNING(
                        f'  Skipping: latter topic not found: "{latter_title}"'
                    )
                )
                continue

            pages = ContentPage.objects.filter(topics=former_topic).distinct().order_by("title")

            pair_total_pages = 0
            pair_add_and_remove = 0
            pair_remove_only = 0

            if not pages.exists():
                self.stdout.write("  No pages currently tagged with former topic.")
                continue

            for page in pages:
                already_has_latter = page.topics.filter(pk=latter_topic.pk).exists()

                pair_total_pages += 1
                grand_total_pages += 1

                if already_has_latter:
                    pair_remove_only += 1
                    grand_total_remove_only += 1
                    action = "remove former only"
                else:
                    pair_add_and_remove += 1
                    grand_total_add_and_remove += 1
                    action = "add latter and remove former"

                if dry_run:
                    self.stdout.write(f'  [dry-run] {page.title}: {action}')
                    continue

                if not already_has_latter:
                    page.topics.add(latter_topic)

                page.topics.remove(former_topic)
                page.save()

                self.stdout.write(f"  Updated {page.title}: {action}")

            self.stdout.write(
                f'  Subtotal for "{former_title}" -> "{latter_title}": '
                f"{pair_total_pages} page(s) affected; "
                f"{pair_add_and_remove} add latter/remove former; "
                f"{pair_remove_only} remove former only."
            )

        self.stdout.write("")
        self.stdout.write("Untagging, archiving, and unpublishing topics")

        for topic_title in self.TOPICS_TO_UNTAG_ARCHIVE_UNPUBLISH:
            topic = TopicPage.objects.filter(title=topic_title).first()

            self.stdout.write("")
            self.stdout.write(f'"{topic_title}"')

            if not topic:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping: topic not found: "{topic_title}"')
                )
                continue

            pages = ContentPage.objects.filter(topics=topic).distinct().order_by("title")

            pair_untagged_pages = 0
            pair_pages_left_without_topics = 0

            if not pages.exists():
                self.stdout.write("  No pages currently tagged with this topic.")
            else:
                for page in pages:
                    remaining_topics = page.topics.exclude(pk=topic.pk)
                    will_have_no_topics = not remaining_topics.exists()

                    pair_untagged_pages += 1
                    grand_total_untagged_pages += 1

                    if will_have_no_topics:
                        pair_pages_left_without_topics += 1
                        grand_total_pages_left_without_topics += 1

                        pages_left_without_topics.append(
                            {
                                "page": page,
                                "removed_topic": topic_title,
                            }
                        )

                    if dry_run:
                        if will_have_no_topics:
                            self.stdout.write(
                                f'  [dry-run] {page.title}: remove "{topic_title}"; page will have no topics left'
                            )
                        else:
                            self.stdout.write(
                                f'  [dry-run] {page.title}: remove "{topic_title}"'
                            )
                        continue

                    page.topics.remove(topic)
                    page.save()

                    if will_have_no_topics:
                        self.stdout.write(
                            f'  {page.title}: removed "{topic_title}"; page now has no topics left'
                        )
                    else:
                        self.stdout.write(
                            f'  {page.title}: removed "{topic_title}"'
                        )

            if dry_run:
                self.stdout.write(f'  [dry-run] Would archive topic "{topic_title}"')
                self.stdout.write(f'  [dry-run] Would unpublish topic "{topic_title}"')
            else:
                if topic.archive == TopicPage.ArchiveStatus.UNARCHIVED:
                    topic.archive = TopicPage.ArchiveStatus.ARCHIVED
                    topic.save()
                    self.stdout.write(f'  Archived topic "{topic_title}"')
                else:
                    self.stdout.write(f'  Topic "{topic_title}" was already archived')

                if topic.live:
                    topic.unpublish()
                    self.stdout.write(f'  Unpublished topic "{topic_title}"')
                else:
                    self.stdout.write(f'  Topic "{topic_title}" was already unpublished')

            self.stdout.write(
                f'  Subtotal for "{topic_title}": '
                f"{pair_untagged_pages} page(s) untagged; "
                f"{pair_pages_left_without_topics} page(s) left without topics."
            )

        self.stdout.write("")
        self.stdout.write("Pages left without any topics")

        if pages_left_without_topics:
            for item in pages_left_without_topics:
                page = item["page"]
                removed_topic = item["removed_topic"]

                self.stdout.write(
                    f'  - {page.title} [{page.specific_class.__name__}] — removed "{removed_topic}"'
                )
        else:
            self.stdout.write("  None.")

        self.stdout.write("")
        self.stdout.write(
            f"Grand total replacements: {grand_total_pages} page-topic match(es) affected; "
            f"{grand_total_add_and_remove} add latter/remove former; "
            f"{grand_total_remove_only} remove former only."
        )

        self.stdout.write(
            f"Grand total removals: {grand_total_untagged_pages} page-topic match(es) untagged; "
            f"{grand_total_pages_left_without_topics} page(s) left without topics."
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete. No changes saved."))
        else:
            self.stdout.write(self.style.SUCCESS("Topic tag update complete."))
