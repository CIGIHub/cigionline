# Generated by Django 5.0.6 on 2025-05-08 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_alter_cigionlinerendition_file'),
        ('publications', '0036_alter_t7publicationpage_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationlistpage',
            name='image_banner',
            field=models.ForeignKey(blank=True, help_text='A banner image to be displayed as background of the hero section.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Banner Image'),
        ),
        migrations.AddField(
            model_name='publicationpage',
            name='image_banner',
            field=models.ForeignKey(blank=True, help_text='A banner image to be displayed as background of the hero section.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Banner Image'),
        ),
        migrations.AddField(
            model_name='publicationserieslistpage',
            name='image_banner',
            field=models.ForeignKey(blank=True, help_text='A banner image to be displayed as background of the hero section.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Banner Image'),
        ),
        migrations.AddField(
            model_name='publicationseriespage',
            name='image_banner',
            field=models.ForeignKey(blank=True, help_text='A banner image to be displayed as background of the hero section.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Banner Image'),
        ),
        migrations.AddField(
            model_name='publicationtypepage',
            name='image_banner',
            field=models.ForeignKey(blank=True, help_text='A banner image to be displayed as background of the hero section.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Banner Image'),
        ),
    ]
