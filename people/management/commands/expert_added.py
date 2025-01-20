import csv
from django.core.management.base import BaseCommand
from wagtail.models import Revision
from people.models import PersonPage  # Replace `myapp` with your actual app name
from json import loads

class Command(BaseCommand):
    help = "Analyze Expert type history for PersonPages and export to CSV"

    def handle(self, *args, **kwargs):
        # File paths
        input_file = "names.csv"  # Replace with the actual path to your file
        output_file = "expert_history.csv"

        # Read names from the input file
        with open(input_file, "r") as f:
            # Read lines, clean extra spaces, and strip leading/trailing spaces
            names = [" ".join(line.split()) for line in f.readlines()]

        # Prepare CSV output
        rows = []
        header = ["Name", "Expert Added Dates", "Expert Removed Dates"]
        first_run = True

        for name in names:
            # Query the PersonPage object
            try:
                if first_run:
                    person = PersonPage.objects.get(last_name="Mathur")
                    first_run = False
                else:
                    person = PersonPage.objects.live().get(title=name)
            except PersonPage.DoesNotExist:
                
                self.stdout.write(f"Person not found: {name}")
                # break
                continue

            # Get all revisions for the page
            revisions = Revision.objects.filter(
                content_type=person.specific_class().content_type,
                object_id=person.id,
            ).order_by("created_at")

            # Analyze revisions
            status_changes = []
            was_expert = False

            for revision in revisions:
                # Deserialize the content
                content = revision.content if isinstance(revision.content, dict) else loads(revision.content)

                # Check the person_types field
                person_types = content["person_types"]
                if 4 in person_types and not was_expert:
                    # "Expert" was added
                    status_changes.append(f"Added: {revision.created_at.strftime('%Y-%m-%d')}")
                    was_expert = True
                elif 4 not in person_types and was_expert:
                    # "Expert" was removed
                    status_changes.append(f"Removed: {revision.created_at.strftime('%Y-%m-%d')}")
                    was_expert = False

            # Add data to rows
            rows.append([
                name,
                " | ".join(status_changes),  # Join changes with a vertical bar
            ])

        # Write to CSV
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(rows)

        self.stdout.write(f"CSV export completed: {output_file}")
