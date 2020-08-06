# Generated by Django 3.0.7 on 2020-08-06 19:31

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('menus', '0002_populate_menus'),
        ('wagtailcore', '0045_assign_unlock_grouppagepermission'),
        ('wagtailimages', '0022_uploadedimage'),
        ('research', '0003_topicpage_drupal_taxonomy_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock())], blank=True)),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('feature_subtitle', models.CharField(blank=True, max_length=255)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('social_title', models.CharField(blank=True, max_length=255)),
                ('social_description', models.CharField(blank=True, max_length=255)),
                ('embed_youtube', models.URLField(blank=True)),
                ('event_access', models.IntegerField(choices=[(0, 'Private'), (1, 'Public')], default=1, null=True)),
                ('event_end', models.DateTimeField(blank=True, null=True)),
                ('event_start', models.DateTimeField()),
                ('flickr_album_url', models.URLField(blank=True)),
                ('invitation_type', models.IntegerField(choices=[(0, 'RSVP Required'), (1, 'Invitation Only'), (2, 'No RSVP Required')], default=0)),
                ('location_address1', models.CharField(blank=True, max_length=255, verbose_name='Address (Line 1)')),
                ('location_address2', models.CharField(blank=True, max_length=255, verbose_name='Address (Line 2)')),
                ('location_city', models.CharField(blank=True, max_length=255, verbose_name='City')),
                ('location_country', models.CharField(blank=True, max_length=255, verbose_name='Country')),
                ('location_name', models.CharField(blank=True, max_length=255)),
                ('location_postal_code', models.CharField(blank=True, max_length=32, verbose_name='Postal Code')),
                ('location_province', models.CharField(blank=True, max_length=255, verbose_name='Province/State')),
                ('registration_url', models.URLField(blank=True, max_length=512)),
                ('related_files', wagtail.core.fields.StreamField([('file', wagtail.documents.blocks.DocumentChooserBlock())], blank=True)),
                ('speakers', wagtail.core.fields.StreamField([('speaker', wagtail.core.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('external_speaker', wagtail.core.blocks.CharBlock(required=True))], blank=True)),
                ('twitter_hashtag', models.CharField(blank=True, max_length=64)),
                ('website_button_text', models.CharField(blank=True, help_text='Override the button text for the event website. If empty, the button will read "Event Website".', max_length=64)),
                ('website_url', models.URLField(blank=True, max_length=512)),
                ('drupal_node_id', models.IntegerField(blank=True, null=True)),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Feature image')),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Hero Image')),
                ('image_social', models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Social image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.Menu', verbose_name='Submenu')),
                ('topics', modelcluster.fields.ParentalManyToManyField(blank=True, to='research.TopicPage')),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='EventListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock())], blank=True)),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Hero Image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.Menu', verbose_name='Submenu')),
            ],
            options={
                'verbose_name': 'Event List Page',
            },
            bases=('wagtailcore.page',),
        ),
    ]
