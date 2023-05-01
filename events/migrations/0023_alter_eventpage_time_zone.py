# Generated by Django 4.0 on 2023-05-01 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0022_eventpage_livestream_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventpage',
            name='time_zone',
            field=models.CharField(blank=True, choices=[('US/Hawaii', '(UTC–10:00) Hawaiian Time'), ('America/Los_Angeles', '(UTC–07:00/08:00) Pacific Time'), ('America/Denver', '(UTC–06:00/07:00) Mountain Time'), ('America/Chicago', '(UTC–05:00/06:00) Central Time'), ('America/Toronto', '(UTC–04:00/05:00) Eastern Time'), ('America/Caracas', '(UTC–04:30) Venezuela Time'), ('America/Halifax', '(UTC–03:00/04:00) Atlantic Time'), ('America/Sao_Paulo', '(UTC–03:00) E. South America Time'), ('Atlantic/Cape_Verde', '(UTC–01:00) Cape Verde Time'), ('Europe/London', '(UTC+00:00/01:00) GMT/BST'), ('Europe/Berlin', '(UTC+01:00/02:00) Central European Time'), ('Asia/Beirut', '(UTC+02:00/03:00) Eastern European Time'), ('Europe/Moscow', '(UTC+03:00) Russian Time'), ('Asia/Tehran', '(UTC+02:30/03:30) Iran Time'), ('Asia/Dubai', '(UTC+04:00) Arabian Time'), ('Asia/Kabul', '(UTC+04:30) Afghanistan Time'), ('Asia/Ashgabat', '(UTC+05:00) West Asia Time'), ('Asia/Kolkata', '(UTC+05:30) India Time'), ('Asia/Kathmandu', '(UTC+05:45) Nepal Time'), ('Asia/Yangon', '(UTC+06:30) Myanmar Time'), ('Asia/Bangkok', '(UTC+07:00) SE Asia Time'), ('Asia/Shanghai', '(UTC+08:00) China Time'), ('Asia/Tokyo', '(UTC+09:00) Tokyo Time'), ('Australia/Sydney', '(UTC+10:00/11:00) AUS Eastern Time'), ('Pacific/Auckland', '(UTC+12:00/13:00) New Zealand Time')], default='America/Toronto', max_length=64),
        ),
    ]
