# Generated by Django 3.2.18 on 2024-03-20 17:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0089_log_entry_data_json_null_to_object'),
        ('articles', '0039_create_opinion_series_page'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='articleseriespage',
            options={'verbose_name': 'Essay Series', 'verbose_name_plural': 'Essay Series'},
        ),
        migrations.AlterField(
            model_name='articlepage',
            name='article_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailcore.page', verbose_name='Essay series'),
        ),
    ]
