# Generated by Django 3.2.4 on 2021-07-14 18:15

from django.db import migrations
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0011_articlepage_hide_excerpt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlepage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('accordion', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.RichTextBlock(features=['bold', 'h3', 'h4', 'italic', 'link', 'ol', 'ul'], required=True))])), ('autoplay_video', wagtail.blocks.StructBlock([('video', streams.blocks.VideoBlock(required=False)), ('caption', wagtail.blocks.CharBlock(required=False))])), ('chart', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('embedded_tiktok', wagtail.blocks.URLBlock(help_text='Paste the link to the video here. It should look like this: https://www.tiktok.com/@who/video/6805515697175792901', required=True)), ('external_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('source', wagtail.blocks.CharBlock(required=False))])), ('external_video', streams.blocks.ExternalVideoBlock()), ('extract', streams.blocks.ExtractBlock()), ('highlight_title', streams.blocks.HighlightTitleBlock()), ('image_full_bleed', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('image_scroll', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('poster_block', streams.blocks.PosterBlock(page_type=['publications.PublicationPage'], required=True)), ('pull_quote_left', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False))])), ('pull_quote_right', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False))])), ('recommended', streams.blocks.RecommendedBlock()), ('text_border_block', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('border_colour', wagtail.blocks.CharBlock(required=False))])), ('tool_tip', wagtail.blocks.StructBlock([('anchor', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('name', wagtail.blocks.CharBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('tweet', wagtail.blocks.StructBlock([('tweet_url', wagtail.blocks.URLBlock(help_text='The URL of the tweet. Example: https://twitter.com/CIGIonline/status/1188821562440454144', required=True, verbose_name='Tweet URL'))]))], blank=True),
        ),
    ]
