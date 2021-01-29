# Generated by Django 3.1.5 on 2021-01-29 03:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtaildocs', '0010_document_file_hash'),
        ('publications', '0005_change_publication_type_to_foreign_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationlistpage',
            name='hero_link_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document'),
        ),
        migrations.AddField(
            model_name='publicationlistpage',
            name='hero_link_icon',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='publicationlistpage',
            name='hero_link_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationlistpage',
            name='hero_link_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationpage',
            name='hero_link_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document'),
        ),
        migrations.AddField(
            model_name='publicationpage',
            name='hero_link_icon',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='publicationpage',
            name='hero_link_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationpage',
            name='hero_link_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationserieslistpage',
            name='hero_link_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document'),
        ),
        migrations.AddField(
            model_name='publicationserieslistpage',
            name='hero_link_icon',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='publicationserieslistpage',
            name='hero_link_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationserieslistpage',
            name='hero_link_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='hero_link_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document'),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='hero_link_icon',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='hero_link_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='hero_link_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationtypepage',
            name='hero_link_document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.document'),
        ),
        migrations.AddField(
            model_name='publicationtypepage',
            name='hero_link_icon',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='publicationtypepage',
            name='hero_link_text',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='publicationtypepage',
            name='hero_link_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
