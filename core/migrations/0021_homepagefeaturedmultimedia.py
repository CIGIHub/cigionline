# Generated by Django 3.1.4 on 2020-12-19 12:37

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multimedia', '0012_change_tweet_block_to_url'),
        ('core', '0020_homepagehighlightpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomePageFeaturedMultimedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('featured_multimedia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='multimedia.multimediapage', verbose_name='Multimedia')),
                ('home_page', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='featured_multimedia', to='core.homepage')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
