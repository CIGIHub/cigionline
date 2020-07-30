# Generated by Django 3.0.7 on 2020-07-30 13:41

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0045_assign_unlock_grouppagepermission'),
        ('core', '0012_populate_themes'),
        ('research', '0003_topicpage_drupal_taxonomy_id'),
        ('wagtailimages', '0022_uploadedimage'),
        ('menus', '0002_populate_menus'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultimediaSeriesListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': 'Multimedia Series List Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='MultimediaSeriesPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock())], blank=True)),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('feature_subtitle', models.CharField(blank=True, max_length=255)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('publishing_date', models.DateField()),
                ('social_title', models.CharField(blank=True, max_length=255)),
                ('social_description', models.CharField(blank=True, max_length=255)),
                ('podcast_apple_url', models.URLField(blank=True, help_text='Enter the link to the Apple Podcast landing page for this podcast.', verbose_name='Apple Podcast URL')),
                ('podcast_google_url', models.URLField(blank=True, help_text='Enter the link to the Google Podcast landing page for the podcast.', verbose_name='Google Podcast URL')),
                ('podcast_spotify_url', models.URLField(blank=True, help_text='Enter the link to the Spotify Podcast landing page for the podcast.', verbose_name='Spotify Podcast URL')),
                ('drupal_node_id', models.IntegerField(blank=True, null=True)),
                ('image_banner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Banner Image')),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Feature image')),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Hero Image')),
                ('image_logo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Series Logo')),
                ('image_poster', models.ForeignKey(blank=True, help_text='A poster image which will be used in the highlights section of the homepage.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Poster Image')),
                ('image_social', models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Social image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.Menu', verbose_name='Submenu')),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.Theme')),
                ('topics', modelcluster.fields.ParentalManyToManyField(blank=True, to='research.TopicPage')),
            ],
            options={
                'verbose_name': 'Multimedia Series',
                'verbose_name_plural': 'Multimedia Series',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='MultimediaPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock())], blank=True)),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('feature_subtitle', models.CharField(blank=True, max_length=255)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('publishing_date', models.DateField()),
                ('social_title', models.CharField(blank=True, max_length=255)),
                ('social_description', models.CharField(blank=True, max_length=255)),
                ('multimedia_url', models.URLField(blank=True, help_text='The URL of the multimedia source from YouTube or Simplecast.', verbose_name='Multimedia URL')),
                ('video_chapters', wagtail.core.fields.StreamField([('video_chapter', wagtail.core.blocks.StructBlock([('chapter_title', wagtail.core.blocks.CharBlock(required=True)), ('location_time', wagtail.core.blocks.IntegerBlock(required=True)), ('chapter_description', wagtail.core.blocks.TextBlock())]))], blank=True)),
                ('youtube_id', models.CharField(blank=True, help_text='Enter just the YouTube ID for this video. This is the series of letters and numbers found either at www.youtube.com/embed/[here], or www.youtube.com/watch?v=[here]. This is used for the video chaptering below.', max_length=32, verbose_name='YouTube ID')),
                ('drupal_node_id', models.IntegerField(blank=True, null=True)),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Feature image')),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Hero Image')),
                ('image_social', models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Social image')),
                ('multimedia_series', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.Page')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.Menu', verbose_name='Submenu')),
                ('theme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.Theme')),
                ('topics', modelcluster.fields.ParentalManyToManyField(blank=True, to='research.TopicPage')),
            ],
            options={
                'verbose_name': 'Multimedia',
                'verbose_name_plural': 'Multimedia',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='MultimediaListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock())], blank=True)),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image', verbose_name='Hero Image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.Menu', verbose_name='Submenu')),
            ],
            options={
                'verbose_name': 'Multimedia List Page',
            },
            bases=('wagtailcore.page',),
        ),
    ]
