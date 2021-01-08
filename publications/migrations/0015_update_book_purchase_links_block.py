# Generated by Django 3.1.5 on 2021-01-07 21:16

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0014_update_embedded_video_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicationpage',
            name='book_purchase_links',
            field=wagtail.core.fields.StreamField([('purchase_link', wagtail.core.blocks.StructBlock([('url', wagtail.core.blocks.URLBlock(required=True)), ('link_text', wagtail.core.blocks.CharBlock(required=True))]))], blank=True),
        ),
    ]
