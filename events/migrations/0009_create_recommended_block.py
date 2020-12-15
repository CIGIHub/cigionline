# Generated by Django 3.1.4 on 2020-12-10 03:35

from django.db import migrations
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_create_text_border_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlistpage',
            name='body',
            field=wagtail.core.fields.StreamField([('accordion', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=True)), ('text', wagtail.core.blocks.RichTextBlock(required=True)), ('columns', wagtail.core.blocks.ChoiceBlock(choices=[('one', 'One'), ('two', 'Two'), ('three', 'Three')]))])), ('autoplay_video', wagtail.core.blocks.StructBlock([('video', streams.blocks.VideoBlock(required=False)), ('caption', wagtail.core.blocks.CharBlock(required=False))])), ('chart', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('paragraph', streams.blocks.ParagraphBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))])), ('image_full_bleed', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('image_scroll', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('embedded_multimedia', wagtail.core.blocks.StructBlock([('multimedia_url', wagtail.core.blocks.URLBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False))])), ('embedded_tiktok', wagtail.core.blocks.URLBlock(help_text='Paste the link to the video here. It should look like this: https://www.tiktok.com/@who/video/6805515697175792901', required=True)), ('embedded_video', wagtail.core.blocks.StructBlock([('video_url', wagtail.core.blocks.URLBlock(required=True)), ('caption', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('square', 'Square')]))])), ('external_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('source', wagtail.core.blocks.CharBlock(required=False))])), ('external_videos', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=True)), ('video_url', wagtail.core.blocks.URLBlock(required=True))]))), ('highlight_title', wagtail.core.blocks.CharBlock(required=True)), ('inline_video', wagtail.core.blocks.PageChooserBlock(page_type=['multimedia.MultimediaPage'], required=True)), ('pull_quote_left', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False))])), ('pull_quote_right', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False))])), ('recommended', streams.blocks.RecommendedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_background_block', wagtail.core.blocks.RichTextBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=False))])), ('tool_tip', wagtail.core.blocks.StructBlock([('anchor', wagtail.core.blocks.CharBlock(required=True)), ('text', wagtail.core.blocks.RichTextBlock(required=True)), ('name', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('tweet', wagtail.core.blocks.StructBlock([('tweet_id', wagtail.core.blocks.IntegerBlock(help_text='Insert the ID of the tweet. It can be found in the browser URL at the end. Example: https://twitter.com/CIGIonline/status/1188821562440454144 -> The tweet id is 1188821562440454144', required=True, verbose_name='Tweet ID'))]))], blank=True),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='body',
            field=wagtail.core.fields.StreamField([('accordion', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=True)), ('text', wagtail.core.blocks.RichTextBlock(required=True)), ('columns', wagtail.core.blocks.ChoiceBlock(choices=[('one', 'One'), ('two', 'Two'), ('three', 'Three')]))])), ('autoplay_video', wagtail.core.blocks.StructBlock([('video', streams.blocks.VideoBlock(required=False)), ('caption', wagtail.core.blocks.CharBlock(required=False))])), ('chart', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('paragraph', streams.blocks.ParagraphBlock()), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))])), ('image_full_bleed', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('image_scroll', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.core.blocks.BooleanBlock(required=False))])), ('embedded_multimedia', wagtail.core.blocks.StructBlock([('multimedia_url', wagtail.core.blocks.URLBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False))])), ('embedded_tiktok', wagtail.core.blocks.URLBlock(help_text='Paste the link to the video here. It should look like this: https://www.tiktok.com/@who/video/6805515697175792901', required=True)), ('embedded_video', wagtail.core.blocks.StructBlock([('video_url', wagtail.core.blocks.URLBlock(required=True)), ('caption', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.core.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('square', 'Square')]))])), ('external_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('source', wagtail.core.blocks.CharBlock(required=False))])), ('external_videos', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=True)), ('video_url', wagtail.core.blocks.URLBlock(required=True))]))), ('highlight_title', wagtail.core.blocks.CharBlock(required=True)), ('inline_video', wagtail.core.blocks.PageChooserBlock(page_type=['multimedia.MultimediaPage'], required=True)), ('pull_quote_left', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False))])), ('pull_quote_right', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False))])), ('recommended', streams.blocks.RecommendedBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_background_block', wagtail.core.blocks.RichTextBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=False))])), ('tool_tip', wagtail.core.blocks.StructBlock([('anchor', wagtail.core.blocks.CharBlock(required=True)), ('text', wagtail.core.blocks.RichTextBlock(required=True)), ('name', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('tweet', wagtail.core.blocks.StructBlock([('tweet_id', wagtail.core.blocks.IntegerBlock(help_text='Insert the ID of the tweet. It can be found in the browser URL at the end. Example: https://twitter.com/CIGIonline/status/1188821562440454144 -> The tweet id is 1188821562440454144', required=True, verbose_name='Tweet ID'))]))], blank=True),
        ),
    ]
