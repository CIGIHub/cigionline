# Generated by Django 3.0.6 on 2020-05-09 01:40

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0045_assign_unlock_grouppagepermission'),
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
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('title', models.CharField(max_length=32)),
                ('link_url', models.CharField(blank=True, help_text='An external URL (https://...) or an internal URL (/interactives/2019annualreport/). This field is only considered if there is no link page.', max_length=512)),
                ('link_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailcore.Page')),
                ('menu', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='menus.Menu')),
                ('submenu', models.ForeignKey(blank=True, help_text='Related submenu to show in the hamburger menu.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='menus.Menu')),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
