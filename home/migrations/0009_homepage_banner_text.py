# Generated by Django 3.2.18 on 2024-04-16 16:01

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_delete_homepagereplacementfeaturedpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='banner_text',
            field=wagtail.fields.RichTextField(blank=True, null=True, verbose_name='Banner Text'),
        ),
    ]
