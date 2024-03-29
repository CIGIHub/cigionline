# Generated by Django 3.2.4 on 2021-11-22 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0009_auto_20211103_1405'),
        ('promotions', '0003_use_custom_image_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionblock',
            name='podcast_episode',
            field=models.ForeignKey(blank=True, help_text='The podcast episode that should be displayed on the ad block. Leave empty for the latest episode', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='multimedia.multimediapage', verbose_name='Podcast Episode'),
        ),
        migrations.AlterField(
            model_name='promotionblock',
            name='block_type',
            field=models.CharField(choices=[('standard', 'Standard'), ('social', 'Social'), ('wide', 'Wide'), ('podcast_player', 'Podcast Player')], default='standard', max_length=32),
        ),
    ]
