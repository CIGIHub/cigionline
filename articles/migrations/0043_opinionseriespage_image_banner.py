# Generated by Django 3.2.18 on 2024-04-03 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20230925_1253'),
        ('articles', '0042_auto_20240325_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='opinionseriespage',
            name='image_banner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Banner Image'),
        ),
    ]
