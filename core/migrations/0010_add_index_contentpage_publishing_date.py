# Generated by Django 3.1.7 on 2021-04-23 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_contentpage_authors_editors_orderable'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='contentpage',
            index=models.Index(fields=['publishing_date'], name='core_conten_publish_56b7a5_idx'),
        ),
    ]
