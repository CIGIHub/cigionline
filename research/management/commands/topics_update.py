import csv

from django.core.management.base import BaseCommand
from wagtail.models import Page

from research.models import ContentPage, TopicPage


class Command(BaseCommand):
    help = "Update topic tags on all tagged content pages."

    TOPIC_REPLACEMENTS = {
        "Gender": "Human Rights",
        "Digital Rights": "Digital Governance",
        "Global Cooperation": "Geopolitics",
        "G20/G7": "Multilateral Institutions",
        "Foreign Interference": "Democracy",
    }

    TOPICS_TO_UNTAG_ARCHIVE_UNPUBLISH = [
        "Surveillance",
        "Competition",
        "Freedom of Thought",
        "Space Governance",
    ]

    NEW_TOPIC_TITLE = "India, China and Africa"
    PROGRAM_TITLE = "Next-Generation Economies"
    TOPICS_PARENT_TITLE = "Topics"

    DEFAULT_CSV_PATH = "pages_left_without_topics.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without saving.",
        )
        parser.add_argument(
            "--csv-path",
            default=self.DEFAULT_CSV_PATH,
            help=f'CSV output path. Defaults to "{self.DEFAULT_CSV_PATH}".',
        )

    def get_page_url(self, page):
        return page.full_url or page.url or ""

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        csv_path = options["csv_path"]

        grand_total_pages = 0
        grand_total_add_and_remove = 0
        grand_total_remove_only = 0

        grand_total_untagged_pages = 0
        grand_total_pages_left_without_topics = 0

        pages_left_without_topics = []
        removed_topic_pks_by_page_pk = {}

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
                    removed_topic_pks = removed_topic_pks_by_page_pk.setdefault(page.pk, set())
                    simulated_removed_topic_pks = removed_topic_pks | {topic.pk}

                    remaining_topics = page.topics.exclude(pk__in=simulated_removed_topic_pks)
                    will_have_no_topics = not remaining_topics.exists()

                    pair_untagged_pages += 1
                    grand_total_untagged_pages += 1

                    if will_have_no_topics:
                        pair_pages_left_without_topics += 1
                        grand_total_pages_left_without_topics += 1

                        pages_left_without_topics.append(
                            {
                                "title": page.title,
                                "url": self.get_page_url(page),
                                "page_type": page.specific_class.__name__,
                                "previous_topic": topic_title,
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

                        removed_topic_pks.add(topic.pk)
                        continue

                    page.topics.remove(topic)
                    page.save()
                    removed_topic_pks.add(topic.pk)

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
        self.stdout.write("Creating new topic and tagging program pages")

        topic = TopicPage.objects.filter(title=self.NEW_TOPIC_TITLE).first()
        topics_parent = Page.objects.filter(title=self.TOPICS_PARENT_TITLE).first()

        if topic:
            self.stdout.write(f'  Topic already exists: "{self.NEW_TOPIC_TITLE}"')
        elif not topics_parent:
            self.stdout.write(
                self.style.WARNING(
                    f'  Skipping topic creation: parent page not found: "{self.TOPICS_PARENT_TITLE}"'
                )
            )
            topic = None
        elif dry_run:
            self.stdout.write(
                f'  [dry-run] Would create topic "{self.NEW_TOPIC_TITLE}" under "{self.TOPICS_PARENT_TITLE}"'
            )
            topic = None
        else:
            topic = TopicPage(title=self.NEW_TOPIC_TITLE)
            topics_parent.specific.add_child(instance=topic)
            self.stdout.write(f'  Created topic "{self.NEW_TOPIC_TITLE}"')

        program_page = Page.objects.filter(title=self.PROGRAM_TITLE).first()

        if not program_page:
            self.stdout.write(
                self.style.WARNING(
                    f'  Skipping program tagging: program page not found: "{self.PROGRAM_TITLE}"'
                )
            )
        elif dry_run:
            pages = ContentPage.objects.descendant_of(program_page, inclusive=False).distinct().order_by("title")

            pages_to_tag_count = 0
            already_tagged_count = 0

            for page in pages:
                already_tagged = (
                    TopicPage.objects.filter(title=self.NEW_TOPIC_TITLE).exists()
                    and page.topics.filter(title=self.NEW_TOPIC_TITLE).exists()
                )

                if already_tagged:
                    already_tagged_count += 1
                    self.stdout.write(
                        f'  [dry-run] {page.title}: already tagged with "{self.NEW_TOPIC_TITLE}"'
                    )
                else:
                    pages_to_tag_count += 1
                    self.stdout.write(
                        f'  [dry-run] {page.title}: would add "{self.NEW_TOPIC_TITLE}"'
                    )

            self.stdout.write(
                f'  Subtotal for "{self.PROGRAM_TITLE}": '
                f"{pages.count()} descendant content page(s); "
                f"{pages_to_tag_count} would be tagged; "
                f"{already_tagged_count} already tagged."
            )
        elif topic:
            pages = ContentPage.objects.descendant_of(program_page, inclusive=False).distinct().order_by("title")

            pages_tagged_count = 0
            already_tagged_count = 0

            for page in pages:
                if page.topics.filter(pk=topic.pk).exists():
                    already_tagged_count += 1
                    self.stdout.write(
                        f'  {page.title}: already tagged with "{self.NEW_TOPIC_TITLE}"'
                    )
                    continue

                page.topics.add(topic)
                page.save()

                pages_tagged_count += 1
                self.stdout.write(
                    f'  {page.title}: added "{self.NEW_TOPIC_TITLE}"'
                )

            self.stdout.write(
                f'  Subtotal for "{self.PROGRAM_TITLE}": '
                f"{pages.count()} descendant content page(s); "
                f"{pages_tagged_count} tagged; "
                f"{already_tagged_count} already tagged."
            )

        self.stdout.write("")
        self.stdout.write("Pages left without any topics")

        if pages_left_without_topics:
            for item in pages_left_without_topics:
                self.stdout.write(
                    f'  - {item["title"]} [{item["page_type"]}] — removed "{item["previous_topic"]}"'
                )
        else:
            self.stdout.write("  None.")

        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["title", "url", "page_type", "previous_topic"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for item in pages_left_without_topics:
                writer.writerow(item)

        self.stdout.write("")
        self.stdout.write(
            f'CSV written to "{csv_path}" with '
            f"{len(pages_left_without_topics)} page(s) left without topics."
        )

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
