from wagtail.models import Revision
from people.models import PersonPage  # Replace `myapp` with your actual app name
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from json import loads


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Filter PersonPage objects tagged with "Expert"
        expert_pages = PersonPage.objects.filter(position__in=['Senior Fellow', 'Fellow'], archive=0).distinct().live()
        # expert_pages = PersonPage.objects.filter(person_types__name="Research Fellow", archive=0).distinct().live()
        person_page_content_type = ContentType.objects.get_for_model(PersonPage)
        print(expert_pages.count())

        # Iterate through each page
        for page in expert_pages:
            print(page.title)
            # # Get all revisions for the page
            # revisions = Revision.objects.filter(
            #     content_type=person_page_content_type,
            #     object_id=page.id
            # ).order_by("created_at")

            # # Initialize a flag to track when "Expert" is first seen
            # expert_added_date = None

            # for revision in revisions:
            #     # Deserialize the content_json field
            #     content = revision.content

            #     # Check if "person_types" is in the content and contains "Expert"
            #     if "person_types" in content:
            #         person_types = content["person_types"]
            #         if 4 in person_types and not expert_added_date:
            #             # If "Expert" is found and not yet recorded
            #             expert_added_date = revision.created_at
            #             # Print person's name and the date of "Expert" added
            #             print(f"{page.title}, {expert_added_date.strftime('%Y-%m-%d')}")
            #             break  # Stop further checks for this page
