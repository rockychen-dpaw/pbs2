# Generated by Django 2.1.2 on 2018-11-29 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prescription', '0002_auto_20181026_0949'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='non_calm_tenure',
            field=models.NullBooleanField(verbose_name='Non-CALM Act Tenure'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='non_calm_tenure_complete',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Yes'), (2, 'No'), (3, 'Yes and No')], null=True, verbose_name='Can the burn be completed safely without the inclusion of other tenure?'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='non_calm_tenure_included',
            field=models.TextField(blank=True, null=True, verbose_name='Non-CALM Act Tenure Included'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='non_calm_tenure_risks',
            field=models.TextField(blank=True, null=True, verbose_name='Risks based issues if other tenure not included'),
        ),
        migrations.AddField(
            model_name='prescription',
            name='non_calm_tenure_value',
            field=models.TextField(blank=True, null=True, verbose_name='Public Value in Burn'),
        ),
    ]