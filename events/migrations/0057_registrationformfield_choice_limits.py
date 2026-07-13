from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0056_registrationformfield_rich_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrationformfield",
            name="choice_limits",
            field=models.TextField(
                blank=True,
                help_text='Optional per-choice limits, one per line: "Choice label | 10".',
            ),
        ),
    ]
