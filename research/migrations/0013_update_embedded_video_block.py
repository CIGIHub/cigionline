# Generated by Django 3.1.5 on 2021-01-05 18:31

from django.db import migrations
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('research', '0012_update_paragraph_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectpage',
            name='body',
            field=wagtail.core.fields.StreamField([('accordion', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=True)), ('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('columns', wagtail.core.blocks.ChoiceBlock(choices=[('one', 'One'), ('two', 'Two'), ('three', 'Three')]))])), ('autoplay_video', wagtail.core.blocks.StructBlock([('video', streams.blocks.VideoBlock(required=False)), ('caption', wagtail.core.blocks.CharBlock(required=False))])), ('chart', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('paragraph', streams.blocks.ParagraphBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))])), ('image_full_bleed', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('image_scroll', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('embedded_multimedia', wagtail.core.blocks.StructBlock([('multimedia_url', wagtail.core.blocks.URLBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False))])), ('embedded_tiktok', wagtail.core.blocks.URLBlock(help_text='Paste the link to the video here. It should look like this: https://www.tiktok.com/@who/video/6805515697175792901', required=True)), ('embedded_video', wagtail.core.blocks.StructBlock([('video_url', wagtail.core.blocks.URLBlock(required=True)), ('caption', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.core.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('external_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('source', wagtail.core.blocks.CharBlock(required=False))])), ('external_videos', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=True)), ('video_url', wagtail.core.blocks.URLBlock(required=True))]))), ('highlight_title', wagtail.core.blocks.CharBlock(required=True)), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('pull_quote_left', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False))])), ('pull_quote_right', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False))])), ('recommended', streams.blocks.RecommendedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_background_block', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=False))])), ('tool_tip', wagtail.core.blocks.StructBlock([('anchor', wagtail.core.blocks.CharBlock(required=True)), ('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('name', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('tweet', wagtail.core.blocks.StructBlock([('tweet_url', wagtail.core.blocks.URLBlock(help_text='The URL of the tweet. Example: https://twitter.com/CIGIonline/status/1188821562440454144', required=True, verbose_name='Tweet URL'))])), ('poster_block', wagtail.core.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True)), ('igc_timeline', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.CharBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('body', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False)), ('location', wagtail.core.blocks.CharBlock(required=False)), ('countries_represented', wagtail.images.blocks.ImageChooserBlock(required=False)), ('outcomes', wagtail.core.blocks.StreamBlock([('outcome', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.DateBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=False))]))], required=False)), ('witnesses', wagtail.core.blocks.StreamBlock([('witness_date', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.DateBlock(required=False)), ('witnesses', wagtail.core.blocks.StreamBlock([('witnesses_full_session', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('witness_transcript', wagtail.core.blocks.URLBlock(required=False)), ('witness_video', wagtail.core.blocks.URLBlock(required=False))])), ('witness', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('witness_transcript', wagtail.core.blocks.URLBlock(required=False)), ('witness_video', wagtail.core.blocks.URLBlock(required=False))]))]))]))], required=False))]))], blank=True),
        ),
    ]
