# Generated by Django 3.1.1 on 2020-09-14 12:26

from django.db import migrations, models
import django.db.models.deletion
import streams.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0022_uploadedimage'),
        ('wagtailcore', '0052_pagelogentry'),
        ('menus', '0002_populate_menus'),
        ('wagtaildocs', '0010_document_file_hash'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.core.fields.StreamField([('advertisement_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False)), ('url', wagtail.core.blocks.URLBlock(required=True)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('cta', wagtail.core.blocks.ChoiceBlock(choices=[('explore', 'Explore'), ('learn_more', 'Learn More'), ('listen', 'Listen'), ('no_cta', 'No CTA'), ('pdf', 'PDF'), ('read', 'Read'), ('rsvp', 'RSVP'), ('share_facebook', 'Share (Facebook)'), ('share_linkedin', 'Share (LinkedIn)'), ('share_twitter', 'Share (Twitter)'), ('subscribe', 'Subscribe'), ('watch', 'Watch')], verbose_name='CTA'))])), ('content_block', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.PageChooserBlock(required=False)), ('url', wagtail.core.blocks.URLBlock(required=False)), ('title_override', wagtail.core.blocks.CharBlock(required=False)), ('text_override', wagtail.core.blocks.RichTextBlock(required=False)), ('cta', wagtail.core.blocks.ChoiceBlock(choices=[('explore', 'Explore'), ('learn_more', 'Learn More'), ('listen', 'Listen'), ('no_cta', 'No CTA'), ('pdf', 'PDF'), ('read', 'Read'), ('rsvp', 'RSVP'), ('share_facebook', 'Share (Facebook)'), ('share_linkedin', 'Share (LinkedIn)'), ('share_twitter', 'Share (Twitter)'), ('subscribe', 'Subscribe'), ('watch', 'Watch')], verbose_name='CTA')), ('line_separator_above', wagtail.core.blocks.BooleanBlock(verbose_name='Add line separator above block'))])), ('featured_content_block', wagtail.core.blocks.StructBlock([('content', wagtail.core.blocks.PageChooserBlock(required=False)), ('url', wagtail.core.blocks.URLBlock(required=False)), ('title_override', wagtail.core.blocks.CharBlock(required=False)), ('text_override', wagtail.core.blocks.RichTextBlock(required=False)), ('image_override', wagtail.images.blocks.ImageChooserBlock(required=False)), ('cta', wagtail.core.blocks.ChoiceBlock(choices=[('explore', 'Explore'), ('learn_more', 'Learn More'), ('listen', 'Listen'), ('no_cta', 'No CTA'), ('pdf', 'PDF'), ('read', 'Read'), ('rsvp', 'RSVP'), ('share_facebook', 'Share (Facebook)'), ('share_linkedin', 'Share (LinkedIn)'), ('share_twitter', 'Share (Twitter)'), ('subscribe', 'Subscribe'), ('watch', 'Watch')], verbose_name='CTA'))])), ('social_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False))])), ('text_block', wagtail.core.blocks.StructBlock([('title', wagtail.core.blocks.CharBlock(required=False)), ('text', wagtail.core.blocks.RichTextBlock(required=False))]))], blank=True)),
                ('drupal_node_id', models.IntegerField(blank=True, null=True)),
                ('html_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document')),
            ],
            options={
                'verbose_name': 'Newsletter',
                'verbose_name_plural': 'Newsletters',
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='NewsletterListPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.core.fields.StreamField([('paragraph', streams.blocks.ParagraphBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('block_quote', wagtail.core.blocks.StructBlock([('quote', wagtail.core.blocks.RichTextBlock(required=True)), ('quote_author', wagtail.core.blocks.CharBlock(required=False)), ('author_title', wagtail.core.blocks.CharBlock(required=False)), ('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('link_url', wagtail.core.blocks.URLBlock(required=False)), ('link_text', wagtail.core.blocks.CharBlock(required=False))])), ('table', wagtail.contrib.table_block.blocks.TableBlock()), ('text_border_block', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(required=True)), ('border_colour', wagtail.core.blocks.CharBlock(required=True))]))], blank=True)),
                ('subtitle', wagtail.core.fields.RichTextField(blank=True)),
                ('image_hero', models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image')),
                ('submenu', models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu')),
            ],
            options={
                'verbose_name': 'Newsletter List Page',
            },
            bases=('wagtailcore.page',),
        ),
    ]
