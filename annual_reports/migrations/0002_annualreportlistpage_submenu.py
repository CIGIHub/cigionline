# Generated by Django 3.1.7 on 2021-03-02 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('annual_reports', '0001_initial'),
        ('menus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='annualreportlistpage',
            name='submenu',
            field=models.ForeignKey(blank=True, help_text='Select a submenu to appear in the right section of the hero.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='menus.menu', verbose_name='Submenu'),
        ),
    ]
