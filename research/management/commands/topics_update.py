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

    COMPETITION_RETAG_SUGGESTIONS = {
        "Are Canada's competition laws outdated? Some say it's time for change": "Digital Economy",
        "Canadian Productivity Lecture Series Aims to Address Declining Standard of Living": "Emerging Technologies",
        "Canadians Deserve Laws That Better Protect Competition": "Digital Economy",
        "Competing Ideas: Canada’s Competition Reform Conversation": "Digital Economy",
        "Competition Bureau remains firm in its decision to challenge proposed Rogers-Shaw merger": "Digital Economy",
        "Competition Policy Explained": "Digital Economy",
        "From Brain Drain to Brain Gain: How India Can Outflank the US in AI": "Artificial Intelligence",
        "Is Competition Tribunal’s Decision on Rogers-Shaw on a Collision Course with the CRTC?": "Digital Economy",
        "Ottawa Rejects Part of Rogers-Shaw Deal": "Digital Economy",
        "Proposed Amendments to Canada’s Competition Act Should Go Further": "Digital Economy",
        "The Canadian business playing field isn’t as fair as you think": "Digital Economy",
        "The Canadian Standard of Living, Productivity and Innovation Lecture Series": "Emerging Technologies",
        "The Competition Cage Match (Vass Bednar and Denise Hearn weigh in)": "Digital Economy",
        "The DOJ’s Action against Google’s Monopoly Is Long Overdue": "Platform Governance",
        "The Next Battleground for the Rogers-Shaw Merger Will Be the CRTC": "Digital Economy",
        "What Is the Competition Bureau’s Vision for the Future of Competition Policy?": "Digital Economy",
        "What’s Ahead for Canada’s Telecom Policy After Rogers-Shaw?": "Digital Economy",
        "Why Canada’s Housing Crisis Is a Productivity Crisis, Too": "Digital Economy",
    }

    NEW_TOPIC_TITLE = "India, China and Africa"
    PROGRAM_TITLE = "Next-Generation Economies: Middle Powers in a Changing World"
    TOPICS_PARENT_TITLE = "Topics"

    DEFAULT_CSV_PATH = "competition_pages_left_without_topics.csv"
    DEFAULT_CHANGE_LOG_CSV_PATH = "topic_tag_update_changes.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show changes without saving.",
        )

        parser.add_argument(
            "--write-csv",
            action="store_true",
            help="Write a CSV of Competition pages left without topics before suggestions are applied.",
        )

        parser.add_argument(
            "--csv-path",
            default=self.DEFAULT_CSV_PATH,
            help=f'CSV output path when --write-csv is used. Defaults to "{self.DEFAULT_CSV_PATH}".',
        )

        parser.add_argument(
            "--write-change-log-csv",
            action="store_true",
            help="Write a CSV log of all verbose change messages.",
        )

        parser.add_argument(
            "--change-log-csv-path",
            default=self.DEFAULT_CHANGE_LOG_CSV_PATH,
            help=(
                "CSV output path when --write-change-log-csv is used. "
                f'Defaults to "{self.DEFAULT_CHANGE_LOG_CSV_PATH}".'
            ),
        )

    def get_page_url(self, page):
        return page.full_url or page.url or ""

    def get_page_type(self, page):
        return page.specific_class.__name__

    def log_change(self, section, page, action, dry_run=False):
        prefix = "[dry-run] " if dry_run else ""
        page_url = self.get_page_url(page)

        self.stdout.write(f"  {prefix}{page.title} ({page_url}): {action}")

        return {
            "dry_run": dry_run,
            "section": section,
            "title": page.title,
            "url": page_url,
            "page_type": self.get_page_type(page),
            "action": action,
        }

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        write_csv = options["write_csv"]
        csv_path = options["csv_path"]
        write_change_log_csv = options["write_change_log_csv"]
        change_log_csv_path = options["change_log_csv_path"]

        change_log_rows = []

        grand_total_pages = 0
        grand_total_add_and_remove = 0
        grand_total_remove_only = 0

        grand_total_untagged_pages = 0
        grand_total_competition_pages_left_without_topics = 0

        competition_pages_left_without_topics = []
        competition_pages_to_retag = []

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
                    change_log_rows.append(
                        self.log_change(
                            section="topic_replacement",
                            page=page,
                            action=action,
                            dry_run=True,
                        )
                    )
                    continue

                if not already_has_latter:
                    page.topics.add(latter_topic)

                page.topics.remove(former_topic)
                page.save()

                change_log_rows.append(
                    self.log_change(
                        section="topic_replacement",
                        page=page,
                        action=action,
                        dry_run=False,
                    )
                )

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
            pair_competition_pages_left_without_topics = 0

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

                    if topic_title == "Competition":
                        suggested_topic_title = self.COMPETITION_RETAG_SUGGESTIONS.get(page.title)

                        if suggested_topic_title:
                            competition_pages_to_retag.append(
                                {
                                    "page": page,
                                    "suggested_topic_title": suggested_topic_title,
                                }
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  No retag suggestion found for Competition page: '
                                    f'{page.title} ({self.get_page_url(page)})'
                                )
                            )

                        if will_have_no_topics:
                            pair_competition_pages_left_without_topics += 1
                            grand_total_competition_pages_left_without_topics += 1

                            competition_pages_left_without_topics.append(
                                {
                                    "title": page.title,
                                    "url": self.get_page_url(page),
                                    "page_type": self.get_page_type(page),
                                    "current_topic": topic_title,
                                }
                            )

                    if will_have_no_topics:
                        action = f'remove "{topic_title}"; page will have no topics left'
                    else:
                        action = f'remove "{topic_title}"'

                    if dry_run:
                        change_log_rows.append(
                            self.log_change(
                                section="topic_removal",
                                page=page,
                                action=action,
                                dry_run=True,
                            )
                        )

                        removed_topic_pks.add(topic.pk)
                        continue

                    page.topics.remove(topic)
                    page.save()
                    removed_topic_pks.add(topic.pk)

                    if will_have_no_topics:
                        real_action = f'removed "{topic_title}"; page now has no topics left'
                    else:
                        real_action = f'removed "{topic_title}"'

                    change_log_rows.append(
                        self.log_change(
                            section="topic_removal",
                            page=page,
                            action=real_action,
                            dry_run=False,
                        )
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

            if topic_title == "Competition":
                self.stdout.write(
                    f'  Subtotal for "{topic_title}": '
                    f"{pair_untagged_pages} page(s) untagged; "
                    f"{pair_competition_pages_left_without_topics} page(s) left without topics before suggestions."
                )
            else:
                self.stdout.write(
                    f'  Subtotal for "{topic_title}": '
                    f"{pair_untagged_pages} page(s) untagged."
                )

        self.stdout.write("")
        self.stdout.write("Competition pages left without any topics before suggestions")

        if competition_pages_left_without_topics:
            for item in competition_pages_left_without_topics:
                self.stdout.write(
                    f'  - {item["title"]} ({item["url"]}) '
                    f'[{item["page_type"]}] — removed "{item["current_topic"]}"'
                )
        else:
            self.stdout.write("  None.")

        if write_csv:
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = ["title", "url", "page_type", "current_topic"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for item in competition_pages_left_without_topics:
                    writer.writerow(item)

            self.stdout.write("")
            self.stdout.write(
                f'CSV written to "{csv_path}" with '
                f"{len(competition_pages_left_without_topics)} Competition page(s) left without topics before suggestions."
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                "CSV not written. Use --write-csv to export Competition pages left without topics before suggestions."
            )

        self.stdout.write("")
        self.stdout.write("Retagging Competition pages from suggestions")

        competition_retagged_count = 0
        competition_already_tagged_count = 0
        competition_missing_topic_count = 0

        if not competition_pages_to_retag:
            self.stdout.write("  No Competition pages queued for retagging.")
        else:
            for item in competition_pages_to_retag:
                page = item["page"]
                suggested_topic_title = item["suggested_topic_title"]

                suggested_topic = TopicPage.objects.filter(title=suggested_topic_title).first()

                if not suggested_topic:
                    competition_missing_topic_count += 1

                    self.stdout.write(
                        self.style.WARNING(
                            f'  Skipping retag for {page.title} ({self.get_page_url(page)}): '
                            f'suggested topic not found: "{suggested_topic_title}"'
                        )
                    )
                    continue

                if page.topics.filter(pk=suggested_topic.pk).exists():
                    competition_already_tagged_count += 1

                    change_log_rows.append(
                        self.log_change(
                            section="competition_suggestion_retag",
                            page=page,
                            action=f'already tagged with "{suggested_topic_title}" after removing "Competition"',
                            dry_run=dry_run,
                        )
                    )
                    continue

                if dry_run:
                    competition_retagged_count += 1

                    change_log_rows.append(
                        self.log_change(
                            section="competition_suggestion_retag",
                            page=page,
                            action=f'would add "{suggested_topic_title}" after removing "Competition"',
                            dry_run=True,
                        )
                    )
                    continue

                page.topics.add(suggested_topic)
                page.save()

                competition_retagged_count += 1

                change_log_rows.append(
                    self.log_change(
                        section="competition_suggestion_retag",
                        page=page,
                        action=f'added "{suggested_topic_title}" after removing "Competition"',
                        dry_run=False,
                    )
                )

        self.stdout.write(
            f'  Subtotal for Competition suggestions: '
            f"{competition_retagged_count} page(s) "
            f"{'would be retagged' if dry_run else 'retagged'}; "
            f"{competition_already_tagged_count} already tagged; "
            f"{competition_missing_topic_count} missing suggested topic."
        )

        self.stdout.write("")
        self.stdout.write("Creating new topic and tagging linked project pages")

        india_china_africa_topic = TopicPage.objects.filter(title=self.NEW_TOPIC_TITLE).first()
        topics_parent = Page.objects.filter(title=self.TOPICS_PARENT_TITLE).first()

        if india_china_africa_topic:
            self.stdout.write(f'  Topic already exists: "{self.NEW_TOPIC_TITLE}"')
        elif not topics_parent:
            self.stdout.write(
                self.style.WARNING(
                    f'  Skipping topic creation: parent page not found: "{self.TOPICS_PARENT_TITLE}"'
                )
            )
            india_china_africa_topic = None
        elif dry_run:
            self.stdout.write(
                f'  [dry-run] Would create topic "{self.NEW_TOPIC_TITLE}" under "{self.TOPICS_PARENT_TITLE}"'
            )
            india_china_africa_topic = None
        else:
            india_china_africa_topic = TopicPage(title=self.NEW_TOPIC_TITLE)
            topics_parent.specific.add_child(instance=india_china_africa_topic)
            self.stdout.write(f'  Created topic "{self.NEW_TOPIC_TITLE}"')

        program_page = Page.objects.filter(title=self.PROGRAM_TITLE).first()

        if program_page:
            program_page = program_page.specific

        if not program_page:
            self.stdout.write(
                self.style.WARNING(
                    f'  Skipping project tagging: project page not found: "{self.PROGRAM_TITLE}"'
                )
            )
        else:
            pages = ContentPage.objects.filter(projects=program_page).distinct().order_by("title")

            pages_to_tag_count = 0
            already_tagged_count = 0

            for page in pages:
                already_tagged = page.topics.filter(title=self.NEW_TOPIC_TITLE).exists()

                if already_tagged:
                    already_tagged_count += 1
                    action = f'already tagged with "{self.NEW_TOPIC_TITLE}"'

                    change_log_rows.append(
                        self.log_change(
                            section="project_topic_tagging",
                            page=page,
                            action=action,
                            dry_run=dry_run,
                        )
                    )

                    continue

                pages_to_tag_count += 1

                if dry_run:
                    change_log_rows.append(
                        self.log_change(
                            section="project_topic_tagging",
                            page=page,
                            action=f'would add "{self.NEW_TOPIC_TITLE}"',
                            dry_run=True,
                        )
                    )
                    continue

                if india_china_africa_topic:
                    page.topics.add(india_china_africa_topic)
                    page.save()

                    change_log_rows.append(
                        self.log_change(
                            section="project_topic_tagging",
                            page=page,
                            action=f'added "{self.NEW_TOPIC_TITLE}"',
                            dry_run=False,
                        )
                    )

            action_label = "would be tagged" if dry_run else "tagged"

            self.stdout.write(
                f'  Subtotal for "{self.PROGRAM_TITLE}": '
                f"{pages.count()} linked content page(s); "
                f"{pages_to_tag_count} {action_label}; "
                f"{already_tagged_count} already tagged."
            )

        if write_change_log_csv:
            with open(change_log_csv_path, "w", newline="", encoding="utf-8-sig") as csvfile:
                fieldnames = [
                    "dry_run",
                    "section",
                    "title",
                    "url",
                    "page_type",
                    "action",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()

                for row in change_log_rows:
                    writer.writerow(row)

            self.stdout.write("")
            self.stdout.write(
                f'Change log CSV written to "{change_log_csv_path}" with '
                f"{len(change_log_rows)} row(s)."
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                "Change log CSV not written. Use --write-change-log-csv to export all change messages."
            )

        self.stdout.write("")
        self.stdout.write(
            f"Grand total replacements: {grand_total_pages} page-topic match(es) affected; "
            f"{grand_total_add_and_remove} add latter/remove former; "
            f"{grand_total_remove_only} remove former only."
        )

        self.stdout.write(
            f"Grand total removals: {grand_total_untagged_pages} page-topic match(es) untagged."
        )

        self.stdout.write(
            f"Grand total Competition pages left without topics before suggestions: "
            f"{grand_total_competition_pages_left_without_topics}."
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete. No changes saved."))
        else:
            self.stdout.write(self.style.SUCCESS("Topic tag update complete."))
