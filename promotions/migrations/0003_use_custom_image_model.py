# Generated by Django 3.1.7 on 2021-04-30 18:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
        ('promotions', '0002_promotionblock_drupal_node_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promotionblock',
            name='image_promotion',
            field=models.ForeignKey(blank=True, help_text='The background image of the promotion block.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Promotion Image'),
        ),
        migrations.AlterField(
            model_name='promotionblock',
            name='image_promotion_small',
            field=models.ForeignKey(blank=True, help_text='The background image of the promotion block. Only used for wide promotion blocks as a replacement when screen width is small. Ex. Multimedia landing page wide promotion block.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Promotion Image (Small)'),
        ),
    ]
