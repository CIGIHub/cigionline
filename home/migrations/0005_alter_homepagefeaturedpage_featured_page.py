# Generated by Django 3.2.4 on 2021-08-24 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_alter_twentiethpagesingleton_body'),
        ('home', '0004_create_homepage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepagefeaturedpage',
            name='featured_page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.contentpage', verbose_name='Content Page'),
        ),
    ]
