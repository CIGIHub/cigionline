# Generated by Django 3.2.18 on 2023-05-03 17:42

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0025_alter_homepage_layout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='layout',
            field=wagtail.fields.StreamField([('row', wagtail.blocks.StructBlock([('row', wagtail.blocks.StreamBlock([('article_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['articles.ArticlePage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny_with_image', 'Tiny with Image'), ('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_large', 'Medium Large'), ('large', 'Large')])), ('image_type', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('square', 'Square')]))])), ('publication_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large')])), ('use_hero_image', wagtail.blocks.BooleanBlock(required=False))])), ('article_series_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['articles.ArticleSeriesPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large'), ('large_full', 'Large Full')]))])), ('event_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['events.EventPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large')]))])), ('multimedia_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['multimedia.MultimediaPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])), ('multimedia_type', wagtail.blocks.ChoiceBlock(choices=[('video', 'Video'), ('podcast', 'Podcast')]))])), ('expert_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium')]))])), ('ad_card', wagtail.blocks.StructBlock([('url', wagtail.blocks.URLBlock(required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])), ('type', wagtail.blocks.ChoiceBlock(choices=[('social', 'Social'), ('subscribe', 'Subscribe'), ('generic', 'Generic')])), ('image', wagtail.images.blocks.ImageChooserBlock(required=True))])), ('most_popular', wagtail.blocks.StructBlock([('most_popular_cards', wagtail.blocks.StreamBlock([('article_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['articles.ArticlePage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny_with_image', 'Tiny with Image'), ('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_large', 'Medium Large'), ('large', 'Large')])), ('image_type', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('square', 'Square')]))])), ('publication_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large')])), ('use_hero_image', wagtail.blocks.BooleanBlock(required=False))])), ('article_series_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['articles.ArticleSeriesPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large'), ('large_full', 'Large Full')]))])), ('event_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['events.EventPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large')]))])), ('multimedia_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['multimedia.MultimediaPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])), ('multimedia_type', wagtail.blocks.ChoiceBlock(choices=[('video', 'Video'), ('podcast', 'Podcast')]))])), ('expert_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium')]))]))]))])), ('column_block', wagtail.blocks.StructBlock([('column_cards', wagtail.blocks.StreamBlock([('article_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['articles.ArticlePage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny_with_image', 'Tiny with Image'), ('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_large', 'Medium Large'), ('large', 'Large')])), ('image_type', wagtail.blocks.ChoiceBlock(choices=[('landscape', 'Landscape'), ('square', 'Square')]))])), ('publication_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large')])), ('use_hero_image', wagtail.blocks.BooleanBlock(required=False))])), ('article_series_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['articles.ArticleSeriesPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large'), ('large_full', 'Large Full')]))])), ('event_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['events.EventPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('medium_vertical', 'Medium Vertical'), ('large', 'Large')]))])), ('multimedia_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['multimedia.MultimediaPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large')])), ('multimedia_type', wagtail.blocks.ChoiceBlock(choices=[('video', 'Video'), ('podcast', 'Podcast')]))])), ('expert_card', wagtail.blocks.StructBlock([('page', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('size', wagtail.blocks.ChoiceBlock(choices=[('tiny', 'Tiny'), ('small', 'Small'), ('medium', 'Medium')]))]))]))]))])), ('grouped', wagtail.blocks.BooleanBlock(default=False, help_text='Group cards into rows with a grey background.', required=False))])), ('social_swiper_row', wagtail.blocks.StructBlock([('social_swiper_cards', wagtail.blocks.StreamBlock([('twitter_card', wagtail.blocks.StructBlock([('tweet', wagtail.snippets.blocks.SnippetChooserBlock(required=True, target_model='social.Tweet'))])), ('linkedin_card', wagtail.blocks.StructBlock([('post', wagtail.snippets.blocks.SnippetChooserBlock(required=True, target_model='social.LinkedinPost'))])), ('facebook_card', wagtail.blocks.StructBlock([('post', wagtail.snippets.blocks.SnippetChooserBlock(required=True, target_model='social.FacebookPost'))]))]))]))], blank=True, use_json_field=None),
        ),
    ]
