# Generated by Django 3.1.5 on 2021-01-17 17:41

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtail.search.index


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0052_pagelogentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('slug', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(max_length=32)),
                ('link_url', models.CharField(blank=True, help_text='An external URL (https://...) or an internal URL (/interactives/2019annualreport/). This field is only considered if there is no link page.', max_length=512)),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.page')),
                ('menu', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='menus.menu')),
                ('submenu', models.ForeignKey(blank=True, help_text='Related submenu to show in the hamburger menu.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='menus.menu')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
