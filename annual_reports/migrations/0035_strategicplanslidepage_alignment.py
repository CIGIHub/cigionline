# Generated by Django 5.0.6 on 2025-03-07 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annual_reports', '0034_strategicplanslidepage_strategic_plan_slide_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategicplanslidepage',
            name='alignment',
            field=models.CharField(blank=True, choices=[('left', 'Left'), ('right', 'Right'), ('full', 'Full'), ('none', 'None')], help_text='Alignment of the columns (only for regular slides)', max_length=255),
        ),
    ]
