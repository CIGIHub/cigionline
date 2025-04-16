# Generated by Django 5.0.6 on 2025-04-08 13:35

import wagtail.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('annual_reports', '0044_alter_strategicplanslidepage_strategic_plan_slide_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategicplanslidepage',
            name='strategic_plan_slide_content',
            field=wagtail.fields.StreamField([('column', wagtail.blocks.RichTextBlock()), ('acknowledgements', wagtail.blocks.RichTextBlock()), ('framework_block', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(required=True)), ('subtitle', wagtail.blocks.CharBlock(required=True)), ('text', wagtail.blocks.StreamBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'coloured'], required=False))])), ('colour', wagtail.blocks.ChoiceBlock(choices=[('yellow', 'Yellow'), ('green', 'Green'), ('pink', 'Pink'), ('blue', 'Blue'), ('multi', 'Multi')], required=False))])), ('board', wagtail.blocks.StructBlock([('board_members', wagtail.blocks.StreamBlock([('member', wagtail.blocks.StructBlock([('name', wagtail.blocks.CharBlock(required=True)), ('title', wagtail.blocks.CharBlock(required=True))]))]))]))], blank=True, help_text='Content of the slide'),
        ),
    ]
