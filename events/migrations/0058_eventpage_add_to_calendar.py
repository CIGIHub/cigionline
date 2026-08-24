from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0057_registrationformfield_choice_limits"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventpage",
            name="add_to_calendar",
            field=models.BooleanField(
                default=True,
                help_text="Show this event on the event list page calendar.",
            ),
        ),
    ]
