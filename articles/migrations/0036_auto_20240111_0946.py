# Generated by Django 3.2.18 on 2024-01-11 14:46

from django.db import migrations
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0035_auto_20231211_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlelandingpage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=True))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='articlepage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=True))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))])), ('accordion', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.RichTextBlock(features=['bold', 'h3', 'h4', 'italic', 'link', 'ol', 'ul'], required=True))])), ('autoplay_video', wagtail.blocks.StructBlock([('video', streams.blocks.VideoBlock(required=False)), ('caption', wagtail.blocks.CharBlock(required=False))])), ('chart', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('embedded_tiktok', wagtail.blocks.URLBlock(help_text='Paste the link to the video here. It should look like this: https://www.tiktok.com/@who/video/6805515697175792901', required=True)), ('external_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('source', wagtail.blocks.CharBlock(required=False))])), ('external_video', streams.blocks.ExternalVideoBlock()), ('extract', streams.blocks.ExtractBlock()), ('highlight_title', streams.blocks.HighlightTitleBlock()), ('image_full_bleed', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('image_scroll', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('poster_block', streams.blocks.PosterBlock(page_type=['publications.PublicationPage'], required=True)), ('pull_quote_left', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False))])), ('pull_quote_right', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False))])), ('recommended', streams.blocks.RecommendedBlock()), ('text_border_block', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('border_colour', wagtail.blocks.CharBlock(required=False))])), ('tool_tip', wagtail.blocks.StructBlock([('anchor', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('name', wagtail.blocks.CharBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('tweet', wagtail.blocks.StructBlock([('tweet_url', wagtail.blocks.URLBlock(help_text='The URL of the tweet. Example: https://twitter.com/CIGIonline/status/1188821562440454144', required=True, verbose_name='Tweet URL'))])), ('additional_image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('classes', wagtail.blocks.CharBlock(required=False)), ('position', wagtail.blocks.ChoiceBlock(choices=[('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6')])), ('animation', wagtail.blocks.ChoiceBlock(choices=[('vertical', 'Vertical'), ('horizontal', 'Horizontal'), ('zoom', 'Zoom'), ('mouse', 'Mouse'), ('none', 'None')])), ('speed', wagtail.blocks.DecimalBlock(default=0)), ('initial_top', wagtail.blocks.IntegerBlock(default=0)), ('initial_left', wagtail.blocks.IntegerBlock(default=0))])), ('additional_disclaimer', wagtail.blocks.StructBlock([('disclaimer', wagtail.blocks.CharBlock())])), ('linebreak', wagtail.blocks.StructBlock([('type', wagtail.blocks.ChoiceBlock(choices=[('space_series_planets', 'Space Series Planets'), ('space_series_stars', 'Space Series Stars'), ('space_series_orbit', 'Space Series Orbit'), ('space_series_ringed_planet', 'Space Series Ringed Planet')]))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='articleseriespage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=True))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='articletypepage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=True))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True),
        ),
        migrations.AlterField(
            model_name='medialandingpage',
            name='body',
            field=wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=True))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True),
        ),
    ]
