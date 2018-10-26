# Generated by Django 2.1.2 on 2018-10-26 01:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('implementation', '0001_initial'),
        ('prescription', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='way',
            name='prescription',
            field=models.ForeignKey(help_text='Prescription this belongs to.', on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
        migrations.AddField(
            model_name='signinspection',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_signinspection_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='signinspection',
            name='modifier',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_signinspection_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='signinspection',
            name='way',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='implementation.Way', verbose_name='Road/Track/Trail Name'),
        ),
        migrations.AddField(
            model_name='operationaloverview',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_operationaloverview_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='operationaloverview',
            name='modifier',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_operationaloverview_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='operationaloverview',
            name='prescription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
        migrations.AddField(
            model_name='lightingsequence',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_lightingsequence_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lightingsequence',
            name='ignition_types',
            field=models.ManyToManyField(to='implementation.IgnitionType', verbose_name='Planned Core Ignition Type'),
        ),
        migrations.AddField(
            model_name='lightingsequence',
            name='modifier',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_lightingsequence_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lightingsequence',
            name='prescription',
            field=models.ForeignKey(help_text='Prescription this lighting sequence belongs to.', on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
        migrations.AddField(
            model_name='exclusionarea',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_exclusionarea_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exclusionarea',
            name='modifier',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_exclusionarea_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='exclusionarea',
            name='prescription',
            field=models.ForeignKey(help_text='Prescription this exclusion area belongs to.', on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
        migrations.AddField(
            model_name='edgingplan',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_edgingplan_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='edgingplan',
            name='fuel_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='prescription.FuelType', verbose_name='Fuel Type'),
        ),
        migrations.AddField(
            model_name='edgingplan',
            name='modifier',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_edgingplan_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='edgingplan',
            name='prescription',
            field=models.ForeignKey(help_text='Prescription this edging plan belongs to.', on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
        migrations.AddField(
            model_name='burningprescription',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_burningprescription_created', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='burningprescription',
            name='fuel_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='prescription.FuelType', verbose_name='Fuel Type'),
        ),
        migrations.AddField(
            model_name='burningprescription',
            name='modifier',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='implementation_burningprescription_modified', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='burningprescription',
            name='prescription',
            field=models.ForeignKey(help_text='Prescription this fuel schedule belongs to.', on_delete=django.db.models.deletion.PROTECT, to='prescription.Prescription'),
        ),
        migrations.AddField(
            model_name='roadsegment',
            name='traffic_diagram',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='implementation.TrafficControlDiagram', verbose_name='Select Traffic Control Diagram'),
        ),
    ]
