# Generated by Django 3.2.18 on 2024-03-20 15:36

from django.db import migrations, models
import django.db.models.deletion
import streams.blocks
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0003_increase_menu_item_title_length'),
        ('images', '0003_auto_20230925_1253'),
        ('core', '0031_auto_20240209_1333'),
        ('articles', '0038_auto_20240209_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpinionSeriesPage',
            fields=[
                ('contentpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.contentpage')),
                ('body', wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publication_type', wagtail.blocks.PageChooserBlock(help_text='Select a publication type to automatically populate with this type of publications.', page_type=['publications.PublicationTypePage'], required=False)), ('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=False))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True)),
                ('hero_link', wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True)),
                ('subtitle', wagtail.fields.RichTextField(blank=True)),
                ('feature_subtitle', models.CharField(blank=True, max_length=500)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('feature_url', models.URLField(blank=True)),
                ('social_title', models.CharField(blank=True, max_length=255)),
                ('social_description', models.CharField(blank=True, max_length=255)),
                ('from_the_archives', models.BooleanField(default=False, help_text='When enabled, show the "From the Archives" label if content is featured on front page.', verbose_name='From the Archives')),
                ('from_the_archives_blurb', wagtail.fields.RichTextField(blank=True, help_text='Block displayed on page.', verbose_name='From the Archives Blurb')),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Feature image')),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Hero Image')),
                ('image_social', models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Social image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu')),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.theme')),
            ],
            options={
                'verbose_name': 'Opinion Series',
                'verbose_name_plural': 'Opinion Series',
            },
            bases=('core.contentpage', models.Model),
        ),
        migrations.CreateModel(
            name='OpinionSeriesListPage',
            fields=[
                ('contentpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.contentpage')),
                ('body', wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', streams.blocks.TableStreamBlock()), ('text_background_block', streams.blocks.TextBackgroundBlock(features=['bold', 'italic', 'link'])), ('persons_list_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=False)), ('bio_source_field', wagtail.blocks.ChoiceBlock(choices=[('full_bio', 'Full Biography'), ('short_bio', 'Short Biography')], help_text="Select the field from the person's page to populate their biography in this block. Default to 'Full Biography'.", max_choices=1, required=False, verbose_name='Biography Source Field')), ('persons', wagtail.blocks.StreamBlock([('person', wagtail.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], required=True))])), ('publications_list_block', wagtail.blocks.StructBlock([('publication_type', wagtail.blocks.PageChooserBlock(help_text='Select a publication type to automatically populate with this type of publications.', page_type=['publications.PublicationTypePage'], required=False)), ('publications', wagtail.blocks.StreamBlock([('publication', wagtail.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True))], required=False))])), ('additional_pages_block', wagtail.blocks.StructBlock([('pages', wagtail.blocks.StreamBlock([('page', wagtail.blocks.PageChooserBlock(required=True))], required=True))]))], blank=True, use_json_field=True)),
                ('hero_link', wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.', use_json_field=True)),
                ('subtitle', wagtail.fields.RichTextField(blank=True)),
                ('feature_subtitle', models.CharField(blank=True, max_length=500)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('feature_url', models.URLField(blank=True)),
                ('social_title', models.CharField(blank=True, max_length=255)),
                ('social_description', models.CharField(blank=True, max_length=255)),
                ('from_the_archives', models.BooleanField(default=False, help_text='When enabled, show the "From the Archives" label if content is featured on front page.', verbose_name='From the Archives')),
                ('from_the_archives_blurb', wagtail.fields.RichTextField(blank=True, help_text='Block displayed on page.', verbose_name='From the Archives Blurb')),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Feature image')),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Hero Image')),
                ('image_social', models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Social image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu')),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.theme')),
            ],
            options={
                'verbose_name': 'Opinion Series List Page',
            },
            bases=('core.contentpage', models.Model),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='opinion_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='articles.opinionseriespage'),
        ),
    ]
