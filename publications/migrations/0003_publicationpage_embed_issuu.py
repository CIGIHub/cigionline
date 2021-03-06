# Generated by Django 3.1.5 on 2021-01-20 23:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20210118_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationpage',
            name='embed_issuu',
            field=models.URLField(blank=True, help_text='Enter the Issuu URL (https://issuu.com/cigi/docs/modern_conflict_and_ai_web) to add an embedded Issuu document.', verbose_name='Issuu Embed'),
        ),
    ]
