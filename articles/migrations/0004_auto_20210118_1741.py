# Generated by Django 3.1.5 on 2021-01-18 22:41

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0003_auto_20210118_1741'),
        ('research', '0001_initial'),
        ('wagtailmedia', '0004_duration_optional_floatfield'),
        ('menus', '0001_initial'),
        ('articles', '0003_auto_20210118_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlepage',
            name='projects',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='research.ProjectPage'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='theme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.theme'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='video_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailmedia.media', verbose_name='Banner Video'),
        ),
        migrations.AddField(
            model_name='articlelandingpagefeaturedarticle',
            name='article_landing_page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_articles', to='articles.articlelandingpage'),
        ),
        migrations.AddField(
            model_name='articlelandingpagefeaturedarticle',
            name='article_page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='articles.articlepage', verbose_name='Article'),
        ),
    ]
