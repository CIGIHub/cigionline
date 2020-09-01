# Generated by Django 3.1 on 2020-08-26 15:18

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0005_populate_project_types'),
        ('people', '0012_add_new_body_paragraphs'),
    ]

    operations = [
        migrations.AddField(
            model_name='personpage',
            name='projects',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='research.ProjectPage'),
        ),
    ]
