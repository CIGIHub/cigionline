from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0002_populate-person-types'),
    ]

    operations = [
        UnaccentExtension(),
    ]
