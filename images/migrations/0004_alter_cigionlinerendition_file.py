# Generated by Django 5.0.6 on 2024-07-25 14:56

import wagtail.images.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20230925_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cigionlinerendition',
            name='file',
            field=wagtail.images.models.WagtailImageField(height_field='height', storage=wagtail.images.models.get_rendition_storage, upload_to=wagtail.images.models.get_rendition_upload_to, width_field='width'),
        ),
    ]
