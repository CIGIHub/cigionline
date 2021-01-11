# Generated by Django 3.1.5 on 2021-01-08 16:45

from django.db import migrations
import streams.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_update_embedded_video_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpage',
            name='speakers',
            field=wagtail.core.fields.StreamField([('speaker', streams.blocks.SpeakersBlock(page_type=['people.PersonPage'], required=True)), ('external_speaker', streams.blocks.ExternalSpeakerBlock())], blank=True),
        ),
    ]
