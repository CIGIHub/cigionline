# Generated by Django 3.1.5 on 2021-02-02 02:35

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.documents.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_change_publication_type_to_foreign_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationlistpage',
            name='hero_link',
            field=wagtail.core.fields.StreamField([('hero_link', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.'),
        ),
        migrations.AddField(
            model_name='publicationpage',
            name='hero_link',
            field=wagtail.core.fields.StreamField([('hero_link', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.'),
        ),
        migrations.AddField(
            model_name='publicationserieslistpage',
            name='hero_link',
            field=wagtail.core.fields.StreamField([('hero_link', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.'),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='hero_link',
            field=wagtail.core.fields.StreamField([('hero_link', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.'),
        ),
        migrations.AddField(
            model_name='publicationtypepage',
            name='hero_link',
            field=wagtail.core.fields.StreamField([('hero_link', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_url', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))])), ('hero_document', wagtail.core.blocks.StructBlock([('hero_link_text', wagtail.core.blocks.CharBlock(required=True)), ('hero_link_document', wagtail.documents.blocks.DocumentChooserBlock(required=True)), ('hero_link_icon', wagtail.core.blocks.CharBlock(help_text='Use a font-awesome icon name such as fa-envelope', required=False))]))], blank=True, help_text='Text with link to url, email or document and optional icon that appears below the page title in the hero section.'),
        ),
    ]
