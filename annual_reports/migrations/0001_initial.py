# Generated by Django 3.1.7 on 2021-03-02 17:16

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('wagtailcore', '0052_pagelogentry'),
        ('wagtaildocs', '0012_uploadeddocument'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnualReportPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('feature_subtitle', models.CharField(blank=True, max_length=255)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('search_terms', wagtail.fields.StreamField([('search_term', wagtail.blocks.CharBlock())], blank=True, help_text='A list of search terms for which this page will be elevated in the search results.')),
                ('report_interactive', models.CharField(blank=True, help_text='Internal path to the interactive report. Example: /interactives/2019annualreport', max_length=255)),
                ('year', models.IntegerField(validators=[django.core.validators.MinValueValidator(2005), django.core.validators.MaxValueValidator(2050)])),
                ('drupal_node_id', models.IntegerField(blank=True, null=True)),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Feature image')),
                ('image_poster', models.ForeignKey(blank=True, help_text='Poster sized image that is displayed in the featured section on the Annual Reports page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Cover image')),
                ('report_english', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document')),
                ('report_financial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document')),
                ('report_french', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document')),
            ],
            options={
                'verbose_name': 'Annual Report Page',
                'verbose_name_plural': 'Annual Report Pages',
            },
            bases=('wagtailcore.page', models.Model),
        ),
        migrations.CreateModel(
            name='AnnualReportListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.StreamField([('block_quote', wagtail.blocks.StructBlock([('quote', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'], required=True)), ('quote_author', wagtail.blocks.CharBlock(required=False)), ('author_title', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.blocks.URLBlock(required=False)), ('link_text', wagtail.blocks.CharBlock(required=False))])), ('embedded_multimedia', wagtail.blocks.StructBlock([('multimedia_url', wagtail.blocks.URLBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=False))])), ('embedded_video', wagtail.blocks.StructBlock([('video_url', wagtail.blocks.URLBlock(required=True)), ('caption', wagtail.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('aspect_ratio', wagtail.blocks.ChoiceBlock(choices=[('none', 'None'), ('landscape', 'Landscape'), ('square', 'Square')]))])), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=True)), ('hide_image_caption', wagtail.blocks.BooleanBlock(required=False))])), ('inline_video', streams.blocks.InlineVideoBlock(page_type=['multimedia.MultimediaPage'])), ('paragraph', streams.blocks.ParagraphBlock()), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_background_block', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link']))], blank=True)),
                ('hero_link', wagtail.fields.StreamField([('hero_link', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.blocks.StructBlock([('hero_link_text', wagtail.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.')),
                ('subtitle', wagtail.fields.RichTextField(blank=True)),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image')),
            ],
            options={
                'verbose_name': 'Annual Report List Page',
            },
            bases=('wagtailcore.page', models.Model),
        ),
    ]
