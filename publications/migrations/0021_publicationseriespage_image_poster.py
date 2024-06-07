# Generated by Django 3.2.18 on 2024-05-16 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20230925_1253'),
        ('publications', '0020_auto_20240209_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationseriespage',
            name='image_poster',
            field=models.ForeignKey(blank=True, help_text='A poster image which will be used in the highlights section of the homepage.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Poster image'),
        ),
    ]
