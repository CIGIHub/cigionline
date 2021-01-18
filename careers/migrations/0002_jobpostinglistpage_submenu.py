# Generated by Django 3.1.5 on 2021-01-17 18:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('careers', '0001_initial'),
        ('menus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpostinglistpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
    ]
