# Generated by Django 3.0.6 on 2020-05-11 15:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0002_populate_menus'),
        ('people', '0009_update_image_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='personlistpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.Menu', verbose_name='Submenu'),
        ),
    ]
