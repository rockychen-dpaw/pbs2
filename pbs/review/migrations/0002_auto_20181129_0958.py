# Generated by Django 2.1.2 on 2018-11-29 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prescribedburn',
            name='region',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Goldfields'), (2, 'Kimberley'), (3, 'Midwest'), (4, 'Pilbara'), (5, 'South Coast'), (6, 'South West'), (7, 'Swan'), (8, 'Warren'), (9, 'Wheatbelt')], null=True),
        ),
    ]