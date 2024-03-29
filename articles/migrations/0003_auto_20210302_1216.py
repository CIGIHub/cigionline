# Generated by Django 3.1.7 on 2021-03-02 17:16

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('wagtailmedia', '0004_duration_optional_floatfield'),
        ('articles', '0002_articlepage_articleserieslistpage_articleseriespage_articletypepage_medialandingpage'),
        ('menus', '0001_initial'),
        ('core', '0001_initial'),
        ('wagtailcore', '0052_pagelogentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='medialandingpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='articletypepage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image'),
        ),
        migrations.AddField(
            model_name='articletypepage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='image_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Banner Image'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='image_banner_small',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Banner Image Small'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='image_feature',
            field=models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Feature image'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='image_poster',
            field=models.ForeignKey(blank=True, help_text='A poster image which will be used in the highlights section of the homepage.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Poster image'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='image_social',
            field=models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Social image'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='theme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.theme'),
        ),
        migrations.AddField(
            model_name='articleseriespage',
            name='video_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailmedia.media', verbose_name='Banner Video'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='article_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.page', verbose_name='Opinion series'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='article_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='articles.articletypepage'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='image_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Banner Image'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='image_banner_small',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Banner Image Small'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='image_feature',
            field=models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Feature image'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='image_social',
            field=models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Social image'),
        ),
        migrations.AddField(
            model_name='articlepage',
            name='multimedia_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.page'),
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
