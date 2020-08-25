# Generated by Django 3.1 on 2020-08-25 14:57

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('wagtailcore', '0052_pagelogentry'),
        ('menus', '0002_populate_menus'),
        ('research', '0003_topicpage_drupal_taxonomy_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'verbose_name': 'Project List Page',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ProjectPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('feature_subtitle', models.CharField(blank=True, max_length=255)),
                ('feature_title', models.CharField(blank=True, max_length=255)),
                ('publishing_date', models.DateField()),
                ('social_title', models.CharField(blank=True, max_length=255)),
                ('social_description', models.CharField(blank=True, max_length=255)),
                ('archive', models.IntegerField(choices=[(0, 'No'), (1, 'Yes')], default=0)),
                ('body', wagtail.core.fields.StreamField([('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=True))])), ('poster_block', wagtail.core.blocks.PageChooserBlock(page_type=['publications.PublicationPage'], required=True)), ('igc_timeline', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.CharBlock(required=True)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('body', wagtail.core.blocks.RichTextBlock(required=False)), ('location', wagtail.core.blocks.CharBlock(required=False)), ('countries_represented', wagtail.images.blocks.ImageChooserBlock(required=False)), ('outcomes', wagtail.core.blocks.StreamBlock([('outcome', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.DateBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False))]))], required=False)), ('witnesses', wagtail.core.blocks.StreamBlock([('witness_date', wagtail.core.blocks.StructBlock([('date', wagtail.core.blocks.DateBlock(required=False)), ('witnesses', wagtail.core.blocks.StreamBlock([('witnesses_full_session', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('witness_transcript', wagtail.core.blocks.URLBlock(required=False)), ('witness_video', wagtail.core.blocks.URLBlock(required=False))])), ('witness', wagtail.core.blocks.StructBlock([('name', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('witness_transcript', wagtail.core.blocks.URLBlock(required=False)), ('witness_video', wagtail.core.blocks.URLBlock(required=False))]))]))]))], required=False))]))], blank=True)),
                ('project_contacts', wagtail.core.fields.StreamField([('contact', wagtail.core.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True))], blank=True)),
                ('project_leads', wagtail.core.fields.StreamField([('project_lead', wagtail.core.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('external_project_lead', wagtail.core.blocks.CharBlock(required=True))], blank=True)),
                ('project_members', wagtail.core.fields.StreamField([('project_member', wagtail.core.blocks.PageChooserBlock(page_type=['people.PersonPage'], required=True)), ('external_project_member', wagtail.core.blocks.CharBlock(required=True))], blank=True)),
                ('related_files', wagtail.core.fields.StreamField([('file', wagtail.documents.blocks.DocumentChooserBlock())], blank=True)),
                ('drupal_node_id', models.IntegerField(blank=True, null=True)),
                ('image_feature', models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Feature image')),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image')),
                ('image_social', models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Social image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu')),
                ('topics', modelcluster.fields.ParentalManyToManyField(blank=True, to='research.TopicPage')),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
            bases=('wagtailcore.page',),
        ),
    ]
