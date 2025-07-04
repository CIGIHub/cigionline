# Generated by Django 5.0.6 on 2025-06-25 17:30

import django.db.models.deletion
import streams.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caiai', '0005_alter_caiaiaboutpage_body'),
        ('wagtailcore', '0093_uploadedfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='CAIAIRecommendationsPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock())], blank=True)),
            ],
            options={
                'verbose_name': 'CAIAI Recommendations Page',
            },
            bases=('wagtailcore.page',),
        ),
    ]
