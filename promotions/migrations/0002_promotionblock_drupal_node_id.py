# Generated by Django 3.1.5 on 2021-02-02 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotionblock',
            name='drupal_node_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
