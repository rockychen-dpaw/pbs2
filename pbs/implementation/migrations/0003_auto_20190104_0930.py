# Generated by Django 2.1.2 on 2019-01-04 01:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('implementation', '0002_auto_20181026_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operationaloverview',
            name='prescription',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
    ]