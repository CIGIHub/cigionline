# Generated by Django 3.1.5 on 2021-01-17 17:41

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0001_initial'),
        ('research', '0001_initial'),
        ('menus', '0001_initial'),
        ('wagtailimages', '0022_uploadedimage'),
        ('wagtailcore', '0052_pagelogentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventpage',
            name='projects',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='research.ProjectPage'),
        ),
        migrations.AddField(
            model_name='eventpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
        migrations.AddField(
            model_name='eventlistpagefeaturedevent',
            name='event_list_page',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_events', to='events.eventlistpage'),
        ),
        migrations.AddField(
            model_name='eventlistpagefeaturedevent',
            name='event_page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.page', verbose_name='Event'),
        ),
        migrations.AddField(
            model_name='eventlistpage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.image', verbose_name='Hero Image'),
        ),
        migrations.AddField(
            model_name='eventlistpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
    ]
