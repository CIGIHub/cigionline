# Generated by Django 3.1.7 on 2021-04-30 18:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
        ('events', '0004_update_table_stream_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlistpage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Hero Image'),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='image_feature',
            field=models.ForeignKey(blank=True, help_text='Image used when featuring on landing pages such as the home page', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Feature image'),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='image_hero',
            field=models.ForeignKey(blank=True, help_text='A large image to be displayed prominently on the page.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Hero Image'),
        ),
        migrations.AlterField(
            model_name='eventpage',
            name='image_social',
            field=models.ForeignKey(blank=True, help_text='An image that is used when sharing on social media.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='images.cigionlineimage', verbose_name='Social image'),
        ),
    ]
