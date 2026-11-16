from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_alter_basicpage_body'),
        ('core', '0072_alter_basicpage_body'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='HumanAnalysisStandardPage',
                ),
            ],
        ),
    ]
