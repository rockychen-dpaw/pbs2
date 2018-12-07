import logging
import sys
from datetime import datetime, date, timedelta
from dateutil import tz

from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ValidationError
from django.utils import timezone

from dpaw_utils.models import AuditMixin

from pbs.prescription.models import (Prescription, Region, District, Tenure)


logger = logging.getLogger('pbs')
# Create your models here.
def current_finyear():
    return datetime.now().year if datetime.now().month>6 else datetime.now().year-1

class BurnState(models.Model):
    fmt = "%d/%m/%Y %H:%M:%S"

    prescription = models.ForeignKey(Prescription, related_name='burnstate', on_delete=models.PROTECT)
    user = models.ForeignKey(User, help_text="User", on_delete=models.PROTECT)
    review_type = models.CharField(max_length=64)
    review_date = models.DateTimeField(auto_now_add=True)

    @property
    def record(self):
        username = '{} {}'.format(self.user.first_name[0], self.user.last_name)
        return "{} {}".format(
            username, self.review_date.astimezone(tz.tzlocal()).strftime(self.fmt)
        )

    def __str__(self):
        return "{} - {} - {}".format(
            self.prescription, self.review_type, self.record)


class ExternalAssist(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class FireTenure(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Acknowledgement(models.Model):
    fmt = "%d/%m/%Y %H:%M"

    burn = models.ForeignKey('PrescribedBurn', related_name='acknowledgements', on_delete=models.PROTECT)
    user = models.ForeignKey(User, help_text="User", null=True, blank=True, on_delete=models.PROTECT)
    acknow_type = models.CharField(max_length=64, null=True, blank=True)
    acknow_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def record(self):
        username = '{} {}'.format(self.user.first_name[0], self.user.last_name)
        return "{} {}".format(
            username, self.acknow_date.astimezone(tz.tzlocal()).strftime(self.fmt)
        )

    def remove(self):
        self.delete()

    def __str__(self):
        return "{} - {} - {}".format(
            self.burn, self.acknow_type, self.record)

class PrescribedBurn(AuditMixin):
    BURN_ACTIVE = 1
    BURN_INACTIVE = 2
    BURN_CHOICES = (
        (BURN_ACTIVE, 'Yes'),
        (BURN_INACTIVE, 'No'),
    )

    IGNITION_STATUS_REQUIRED = 1
    IGNITION_STATUS_COMPLETED = 2
    IGNITION_STATUS_CHOICES = (
        (IGNITION_STATUS_REQUIRED, 'Further ignitions required'),
        (IGNITION_STATUS_COMPLETED, 'Ignition now complete'),
    )

    APPROVAL_DRAFT = 'DRAFT'
    APPROVAL_SUBMITTED = 'USER'
    APPROVAL_ENDORSED = 'SRM'
    APPROVAL_APPROVED = 'SDO'
    APPROVAL_CHOICES = (
        (APPROVAL_DRAFT, 'Draft'),
        (APPROVAL_SUBMITTED, 'District Submitted'),
        (APPROVAL_ENDORSED, 'Region Endorsed'),
        (APPROVAL_APPROVED, 'State Approved'),
    )

    FORM_268A = 1
    FORM_268B = 2
    FORM_NAME_CHOICES = (
        (FORM_268A, 'Form 268a'),
        (FORM_268B, 'Form 268b'),
    )

    '''
    BUSHFIRE_DISTRICT_ALIASES can be used to override the District's original code from the model. Usage e.g.:
    BUSHFIRE_DISTRICT_ALIASES = {
        'PHS' : 'PH',
        'SWC' : 'SC',
    }
    '''
    BUSHFIRE_DISTRICT_ALIASES = {
    }


    fmt = "%Y-%m-%d %H:%M"

    prescription = models.ForeignKey(Prescription, verbose_name="Burn ID", related_name='prescribed_burn', null=True, blank=True, on_delete=models.PROTECT)
#    prescription = ChainedForeignKey(
#        Prescription, chained_field="region", chained_model_field="region",
#        show_all=False, auto_choose=True, blank=True, null=True)


    # Required for Fire records
    fire_id = models.CharField(verbose_name="Fire Number", max_length=15, null=True, blank=True)
    fire_name = models.TextField(verbose_name="Name", null=True, blank=True)
    region = models.PositiveSmallIntegerField(choices=[(r.id, r.name) for r in Region.objects.all()], null=True, blank=True)
    district = models.ForeignKey(District,blank=True, null=True, on_delete=models.PROTECT)
    fire_tenures = models.ManyToManyField(FireTenure, verbose_name="Tenures", blank=True)
    date = models.DateField(auto_now_add=False)
    form_name = models.PositiveSmallIntegerField(verbose_name="Form Name (268a / 268b)", choices=FORM_NAME_CHOICES, editable=True)
    status = models.PositiveSmallIntegerField(verbose_name="Active", choices=BURN_CHOICES, null=True, blank=True)
    ignition_status = models.PositiveSmallIntegerField(verbose_name="Ignition Status", choices=IGNITION_STATUS_CHOICES, null=True, blank=True)
    external_assist = models.ManyToManyField(ExternalAssist, verbose_name="Assistance received from", blank=True)

    planned_area = models.DecimalField(
        verbose_name="Today's treatment area (ha)", max_digits=12, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    area = models.DecimalField(
        verbose_name="Yesterday's treatment area (ha)", max_digits=12, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)

    planned_distance = models.DecimalField(
        verbose_name="Today's treatment distance (km)", max_digits=12, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    distance = models.DecimalField(
        verbose_name="Yesterday's treatment distance (km)", max_digits=12, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)

    tenures= models.TextField(verbose_name="Tenure")
    location= models.TextField(verbose_name="Location", null=True, blank=True)
    est_start = models.TimeField('Estimated Start Time', null=True, blank=True)
    conditions = models.TextField(verbose_name='SDO Special Conditions', null=True, blank=True)
    rolled = models.BooleanField(verbose_name="Fire Rolled from yesterday", editable=False, default=False)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    #aircraft_burn = models.BooleanField(verbose_name="Aircraft Burn", default=False)

    @property
    def is_acknowledged(self):
        if all(x in [i.acknow_type for i in self.acknowledgements.all()] for x in ['SDO_A','SDO_B']):
            return True
        else:
            return False

    @property
    def user_a_record(self):
        ack = self.acknowledgements.filter(acknow_type='USER_A')
        return ack[0].record if ack else None

    @property
    def srm_a_record(self):
        ack = self.acknowledgements.filter(acknow_type='SRM_A')
        return ack[0].record if ack else None

    @property
    def sdo_a_record(self):
        ack = self.acknowledgements.filter(acknow_type='SDO_A')
        return ack[0].record if ack else None

    @property
    def user_b_record(self):
        ack = self.acknowledgements.filter(acknow_type='USER_B')
        return ack[0].record if ack else None

    @property
    def srm_b_record(self):
        ack = self.acknowledgements.filter(acknow_type='SRM_B')
        return ack[0].record if ack else None

    @property
    def sdo_b_record(self):
        ack = self.acknowledgements.filter(acknow_type='SDO_B')
        return ack[0].record if ack else None

    @property
    def formA_isDraft(self):
        return not any(x in [i.acknow_type for i in self.acknowledgements.all()] for x in ['USER_A', 'SRM_A', 'SDO_A'])

    @property
    def formB_isDraft(self):
        return not any(x in [i.acknow_type for i in self.acknowledgements.all()] for x in ['USER_B', 'SRM_B', 'SDO_B'])

    @property
    def formA_user_acknowledged(self):
        return True if self.user_a_record else False

    @property
    def formA_srm_acknowledged(self):
        return True if self.srm_a_record else False

    @property
    def formA_sdo_acknowledged(self):
        return True if self.sdo_a_record else False

    @property
    def formB_user_acknowledged(self):
        return True if self.user_b_record else False

    @property
    def formB_srm_acknowledged(self):
        return True if self.srm_b_record else False

    @property
    def formB_sdo_acknowledged(self):
        return True if self.sdo_b_record else False

    @property
    def fire_type(self):
        return "Burn" if self.prescription else "Fire"

    @property
    def fire_idd(self):
        if self.prescription:
            return self.prescription.burn_id
        else:
            return self.fire_id

    @property
    def further_ignitions_req(self):
        if self.ignition_status==self.IGNITION_STATUS_REQUIRED:
            return True
        elif self.ignition_status==self.IGNITION_STATUS_COMPLETED:
            return False
        return None


    @property
    def active(self):
        if self.status==self.BURN_ACTIVE:
            return True
        elif self.status==self.BURN_INACTIVE:
            return False
        return None

    @property
    def has_conditions(self):
        if self.conditions:
            return True
        return False

    @property
    def planned_area_str(self):
        _str = ''
        if self.planned_area:
            _str += str(self.planned_area) + " ha {} ".format('-' if self.planned_distance else '')

        if self.planned_distance:
            _str += str(self.planned_distance) + " km"

        return _str

    @property
    def area_str(self):
        _str = ''
        if self.area>=0:
            _str += str(self.area) + " ha {} ".format('-' if self.distance else '')

        if self.distance>=0:
            _str += str(self.distance) + " km"

        return _str

    @property
    def tenures_str(self):
        if self.prescription:
            return self.tenures #', '.join([t.name for t in self.tenures.all()])
        else:
            return ', '.join([i.name for i in self.fire_tenures.all()])

    @property
    def had_external_assist(self):
        if self.external_assist.all().count() > 0:
            return True
        return False

    @property
    def external_assist_str(self):
        return ', '.join([i.name for i in self.external_assist.all()])

    @property
    def name(self):
        if self.prescription:
            return self.prescription.name
        else:
            return self.fire_name

    @property
    def get_region(self):
        return self.prescription.region if self.prescription else self.region

    @property
    def get_district(self):
        return self.prescription.district if self.prescription else self.district

    @property
    def can_endorse(self):
        return (self.status == self.APPROVAL_SUBMITTED)

    @property
    def can_approve(self):
        return (self.status == self.APPROVAL_ENDORSED)

    @property
    def last_ignition(self):
        if self.prescription:
            area_achievements = self.prescription.areaachievement_set.all()
            if area_achievements:
                return max([i.ignition for i in area_achievements])
        return None

    def short_str(self):
        return self.prescription.burn_id if self.prescription else self.fire_id

    def copy_ongoing_records(self, dt):
        """
        Copy today's 'active' records to tomorrow

        268b - (Automatically) copy all records from yesterday that were Active when 268a Region Endorsement occurs,
        except for Active and Area Burnt Yesterday

        dt = from date, copied to dt+1
        """

        tomorrow = dt + timedelta(days=1) # relative to dt
        #objects = [obj for obj in PrescribedBur.objects.filter(date=dt, status=PrescribedBurn.BURN_ACTIVE)]
        objects = [self]
        now = timezone.now()
        admin = User.objects.get(username='admin')
        count = 0
        for obj in objects:
            if obj.fire_id and PrescribedBurn.objects.filter(fire_id=obj.fire_id, date=tomorrow, form_name=PrescribedBurn.FORM_268B):
                # don't copy if already exists - since record is unique on Prescription (not fire_id)
                logger.info('Ongoing Record Already Exists (Fire) - not copied (268b today to 268b tomorrow). Record {}, today {}, tomorrow {}'.format(obj.fire_idd, dt, tomorrow))
                continue
            if obj.prescription and PrescribedBurn.objects.filter(prescription__burn_id=obj.prescription.burn_id, date=tomorrow, form_name=PrescribedBurn.FORM_268B, location=obj.location):
                # don't copy if already exists - since record is unique on Prescription (not fire_id)
                logger.info('Ongoing Record Already Exists (Burn) - not copied (268b today to 268b tomorrow). Record {}, today {}, tomorrow {}'.format(obj.fire_idd, dt, tomorrow))
                continue
            try:
                obj.pk = None
                obj.date = tomorrow
                obj.area = None
                obj.status = None
                obj.approval_268a_status = PrescribedBurn.APPROVAL_DRAFT
                obj.approval_268a_status_modified = now
                obj.approval_268b_status = PrescribedBurn.APPROVAL_DRAFT
                obj.approval_268b_status_modified = now
                obj.acknowledgements.all().delete()
                obj.rolled = True
                obj.save()
                count += 1
                logger.info('Ongoing Record copied (268b today to 268b tomorrow). Record {}, today {}, tomorrow {}'.format(obj.fire_idd, dt, tomorrow))
            except:
                # records already exist - pk (pres, date) will not allow overwrite, so ignore the exception
                logger.warn('Ongoing Record not copied. Record {} already exists on day {}'.format(obj.fire_idd, tomorrow))

    def copy_planned_approved_records_adhoc(self, dt):
        """
        Copy today's 'planned' records (268a), that have been SDO approved. to tomorrow ongoing (268b)

        set Active and Area Burnt fields to None

        dt = from date, copied to dt+1
        """

        tomorrow = dt + timedelta(days=1) # relative to dt
        if not self.formA_sdo_acknowledged:
            logger.info('Only SDO Acknowledged record can be copied from dt {} to tomorrow {}'.format(dt, tomorrow))
            return

        #objects = PrescribedBurn.objects.filter(date=dt, acknowledgements__acknow_type__in=['SDO_A'], form_name=PrescribedBurn.FORM_268A)
        objects = [self]
        now = timezone.now()
        count = 0
        for obj in objects:
            if obj.fire_id and PrescribedBurn.objects.filter(fire_id=obj.fire_id, date=tomorrow, form_name=PrescribedBurn.FORM_268B):
                # don't copy if already exists - since record is unique on Prescription (not fire_id)
                logger.info('Planned Approved Record Already Exists (Fire) - not copied (268a today to 268b tomorrow). Record {}, today {}, tomorrow {}'.format(obj.fire_idd, dt, tomorrow))
                continue
            if obj.prescription and PrescribedBurn.objects.filter(prescription__burn_id=obj.prescription.burn_id, date=tomorrow, form_name=PrescribedBurn.FORM_268B, location=obj.location):
                # don't copy if already exists - since record is unique on Prescription (not fire_id)
                logger.info('Planned Approved Record Already Exists (Burn) - not copied (268a today to 268b tomorrow). Record {}, today {}, tomorrow {}'.format(obj.fire_idd, dt, tomorrow))
                continue
            try:
                obj.pk = None
                obj.date = tomorrow
                obj.area = None
                obj.distance = None
                obj.status = None
                obj.approval_268a_status = PrescribedBurn.APPROVAL_DRAFT
                obj.approval_268a_status_modified = now
                obj.approval_268b_status = PrescribedBurn.APPROVAL_DRAFT
                obj.approval_268b_status_modified = now
                #obj.acknowledgements.all().delete()
                obj.form_name=PrescribedBurn.FORM_268B
                obj.rolled = True
                obj.save()
                count += 1
                logger.info('Planned Approved Record copied (268a today to 268b tomorrow). Record {}, today {}, tomorrow {}'.format(obj.fire_idd, dt, tomorrow))
            except:
                # records already exist - pk (pres, date) will not allow overwrite, so ignore the exception
                logger.warn('Planned Approved Record not copied. Record {} already exists on day {}'.format(obj.fire_idd, tomorrow))

    def clean_fire_id(self):
        # set the Lat/Long to Zero, since Bushfire is not assigning these required fields
        self.latitude = 0.0
        self.longitude = 0.0

#    def clean_date(self):
#        today = date.today()
#        tomorrow = today + timedelta(days=1)
#        if not self.pk and (self.date < today or self.date > tomorrow):
#            raise ValidationError("You must enter burn plans for today or tommorow's date only.")

    def clean_planned_distance(self):
        if self.planned_area==None and self.planned_distance==None:
            raise ValidationError("Must input at least one of Area or Distance")

    def clean_distance(self):
        if self.area==None and self.distance==None:
            raise ValidationError("Must input at least one of Area or Distance")

    def clean(self):
        if not self.form_name:
            if self.prescription and self.area==None and self.distance==None:
                self.form_name = 1
            else:
                self.form_name = 2

        if self.prescription and not (self.region and self.district):
            self.region = self.prescription.region.id
            self.district = self.prescription.district


    def __str__(self):
        return self.prescription.burn_id + ' (Burn)' if self.prescription else self.fire_id + ' (Fire)'

    class Meta:
        unique_together = ('prescription', 'date', 'form_name', 'location')
        verbose_name = 'Prescribed Burn or Bushfire'
        verbose_name_plural = 'Prescribed Burns and Bushfires'
        permissions = (
            ("can_endorse", "Can endorse burns"),
            ("can_approve", "Can approve burns"),
        )


class AircraftApproval(models.Model):
    fmt = "%d/%m/%Y %H:%M"

    aircraft_burn = models.ForeignKey('AircraftBurn', related_name='approvals', on_delete=models.PROTECT)
    user = models.ForeignKey(User, help_text="User", null=True, blank=True, on_delete=models.PROTECT)
    approval_type = models.CharField(max_length=64, null=True, blank=True)
    approval_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    @property
    def record(self):
        username = '{} {}'.format(self.user.first_name[0], self.user.last_name)
        return "{} {}".format(
            username, self.approval_date.astimezone(tz.tzlocal()).strftime(self.fmt)
        )

    def remove(self):
        self.delete()

    def __str__(self):
        return "{} - {} - {}".format(
            self.aircraft_burn, self.approval_type, self.record)

class AircraftBurn(AuditMixin):
    APPROVAL_DRAFT = 'DRAFT'
    APPROVAL_SUBMITTED = 'USER'
    APPROVAL_ENDORSED = 'SRM'
    APPROVAL_APPROVED = 'SDO'
    APPROVAL_CHOICES = (
        (APPROVAL_DRAFT, 'Draft'),
        (APPROVAL_SUBMITTED, 'District Submitted'),
        (APPROVAL_ENDORSED, 'Region Endorsed'),
        (APPROVAL_APPROVED, 'State Approved'),
    )

    fmt = "%Y-%m-%d %H:%M"

    prescription = models.ForeignKey(Prescription, verbose_name="Burn ID", related_name='aircraft_burns', null=True, blank=True, on_delete=models.PROTECT)
    #prescribed_burn = models.ForeignKey(PrescribedBurn, verbose_name="Daily Burn ID", related_name='aircraft_burn', null=True, blank=True)

    date = models.DateField(auto_now_add=False)
    area = models.DecimalField(
        verbose_name="Area (ha)", max_digits=12, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    est_start = models.TimeField('Estimated Start Time', null=True, blank=True)
    bombing_duration = models.DecimalField(
        verbose_name="Bombing Duration (hrs)", max_digits=5, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    min_smc = models.DecimalField(
        verbose_name="Min SMC", max_digits=5, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    max_fdi = models.DecimalField(
        verbose_name="Max FDI", max_digits=5, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    sdi_per_day = models.DecimalField(
        verbose_name="SDI Each Day", max_digits=5, decimal_places=1,
        validators=[MinValueValidator(0.0)], null=True, blank=True)
    flight_seq= models.TextField(verbose_name="Flight Sequence", null=True, blank=True)
    aircraft_rego= models.TextField(verbose_name="Aircraft Rego", null=True, blank=True)
    arrival_time= models.TimeField(verbose_name="Arrival Time Over Burn", null=True, blank=True)
    program= models.TextField(verbose_name="Program", null=True, blank=True)
    aircrew= models.TextField(verbose_name="Aircrew", null=True, blank=True)

    rolled = models.BooleanField(verbose_name="Fire Rolled from yesterday", editable=False, default=False)
    #location= models.TextField(verbose_name="Location", null=True, blank=True)

    @property
    def regional_approval(self):
        return True

    @property
    def state_duty_approval(self):
        return True

    @property
    def state_aviation_approval(self):
        return True

    def __str__(self):
        return self.prescription.burn_id

    class Meta:
        unique_together = ('prescription', 'date')
        verbose_name = 'Aircraft Burn'
        verbose_name_plural = 'Aircraft Burns'
        permissions = (
            ("can_endorse", "Can endorse burns"),
            ("can_approve", "Can approve burns"),
        )


class AnnualIndicativeBurnProgram(models.Model):
    objectid = models.IntegerField(primary_key=True)
    wkb_geometry = models.MultiPolygonField(srid=4326, blank=True, null=True)
    region = models.CharField(max_length=35, blank=True)
    district = models.CharField(max_length=35, blank=True)
    burnid = models.CharField(max_length=30, blank=True)
    fin_yr = models.CharField(verbose_name='Fin Year', max_length=9, blank=True, null=True)
    location = models.CharField(max_length=254, blank=True)
    status = models.CharField(max_length=254, blank=True)
    priority = models.DecimalField(max_digits=9, decimal_places=0, blank=True, null=True)
    content = models.CharField(max_length=254, blank=True)
    issues = models.CharField(max_length=254, blank=True)
    treatment = models.DecimalField(max_digits=9, decimal_places=0, blank=True, null=True)
    purpose_1 = models.CharField(max_length=254, blank=True)
    program = models.CharField(max_length=254, blank=True)
    acb = models.CharField(max_length=254, blank=True)
    trtd_area = models.CharField(max_length=254, blank=True)
    yslb = models.CharField(max_length=254, blank=True)
    area_ha = models.DecimalField(max_digits=19, decimal_places=11, blank=True, null=True)
    perim_km = models.DecimalField(max_digits=19, decimal_places=11, blank=True, null=True)
    longitude = models.DecimalField(max_digits=19, decimal_places=11, blank=True, null=True)
    latitude = models.DecimalField(max_digits=19, decimal_places=11, blank=True, null=True)
    objects = models.Manager()

class BurnProgramLink(models.Model):
    prescription = models.OneToOneField(Prescription, on_delete=models.CASCADE)
    wkb_geometry = models.MultiPolygonField(srid=4326)
    area_ha = models.FloatField()
    longitude = models.FloatField()
    latitude = models.FloatField()
    perim_km = models.FloatField()
    trtd_area = models.FloatField()

    @classmethod
    def populate(cls):
        # Links prescriptions to burn program records imported using ogr2ogr
        import subprocess
        subprocess.check_call(['ogr2ogr', '-overwrite', '-f', 'PostgreSQL', "PG:dbname='{NAME}' host='{HOST}' port='{PORT}' user='{USER}' password={PASSWORD}".format(**settings.DATABASES["default"]),
            settings.ANNUAL_INDIC_PROGRAM_PATH, '-nln', 'review_annualindicativeburnprogram', '-nlt', 'PROMOTE_TO_MULTI', settings.SHP_LAYER, '-t_srs', 'EPSG:4326'])
        for p in AnnualIndicativeBurnProgram.objects.all():
            try:
                for prescription in Prescription.objects.filter(burn_id=p.burnid, financial_year=p.fin_yr.replace("/", "/20")):
                    if cls.objects.filter(prescription=prescription).exists():
                        obj = cls.objects.get(prescription=prescription)
                    else:
                        obj = cls(prescription=prescription)
                    obj.wkb_geometry = p.wkb_geometry
                    obj.area_ha = p.area_ha
                    obj.longitude = p.longitude
                    obj.latitude = p.latitude
                    obj.perim_km = p.perim_km
                    obj.trtd_area = p.trtd_area if p.trtd_area else 0.0
                    obj.save()
            except:
                logger.error('ERROR: Assigning AnnulaIndicativeBurnProgram \n{}'.format(sys.exc_info()))


        from django.db import connection
        cursor = connection.cursor()
        cursor.execute('''
            create or replace view review_v_dailyburns as
			select
			  p.burn_id,
			  to_char(pb.date, 'FMDay, DD Mon YYYY') as burn_target_date,
			  pb.date as burn_target_date_raw,
			  case
				when string_agg(pb.form_name::text, ', ') = '1, 2' or string_agg(pb.form_name::text, ', ') = '2, 1' then
					'Active - Planned Ignitions Today'
				when string_agg(pb.form_name::text, ', ') = '2' then
					'Active - No Planned Ignitions Today'
				when string_agg(pb.form_name::text, ', ') = '1' then
					'Planned - No Prior Ignitions'
				else
					'Error'
			  end as burn_stat,
			  case
				when pb.location like '%|%' then
					case
						when p.forest_blocks not like '' then
							split_part(pb.location, '|', 1) || ', ' || split_part(pb.location, '|', 2) || 'km ' ||
								split_part(pb.location, '|', 3) || ' of '|| split_part(pb.location, '|', 4) ||
								' (' || p.forest_blocks || ')'
						else
							split_part(pb.location, '|', 1) || ', ' || split_part(pb.location, '|', 2) || 'km ' ||
								split_part(pb.location, '|', 3) || ' of '|| split_part(pb.location, '|', 4)
						end
				else
					case
						when p.forest_blocks not like '' then
							pb.location || ' (' || p.forest_blocks || ')'
						else
							pb.location
						end
			  end as location,
			  p.forest_blocks,
			  link.area_ha AS indicative_area,
			  coalesce(
				(select rpb.est_start
					 from review_prescribedburn rpb
					 where
						  rpb.date = pb.date and
						  rpb.prescription_id::text = pb.prescription_id::text and
						  rpb.form_name = 1 and
						  rpb.location = pb.location)::text,
				'') AS burn_est_start, -- use time from 268a
			  coalesce(
				(select rpb.longitude
				 from review_prescribedburn rpb
				 where
						rpb.date = pb.date and
						rpb.prescription_id::text = pb.prescription_id::text and
						rpb.form_name = 1 and
						rpb.location = pb.location),
				pb.longitude) AS burn_target_long, -- use longitude from 268a, else 268b
			  coalesce(
				(select rpb.latitude
				 from review_prescribedburn rpb
				 where
					rpb.date = pb.date and
					rpb.prescription_id::text = pb.prescription_id::text and
					rpb.form_name = 1 and
					rpb.location = pb.location),
				pb.latitude) AS burn_target_lat, -- use latitude from 268a, else 268b
			  coalesce(
				cast((select rpb.planned_area
				 from review_prescribedburn rpb
				 where
					rpb.date = pb.date and
					rpb.prescription_id::text = pb.prescription_id::text and
					rpb.form_name = 1 and
					rpb.location = pb.location) as text),
				'') AS burn_planned_area_today, -- use planned_area from 268a
			  coalesce(
				cast((select rpb.planned_distance
				 from review_prescribedburn rpb
				 where
					rpb.date = pb.date and
					rpb.prescription_id::text = pb.prescription_id::text and
					rpb.form_name = 1 and
					rpb.location = pb.location) as text),
				'') AS burn_planned_distance_today, -- use planned_distance from 268a
			  link.wkb_geometry,
                          coalesce((SELECT array_to_string(array_agg(pp.name),' , ')
                                    FROM prescription_prescription_purposes ppps JOIN prescription_purpose pp ON ppps.purpose_id = pp.id
                                    WHERE ppps.prescription_id = p.id)
                           ,'') AS burn_purpose
			from
			  (((prescription_prescription p
				 LEFT JOIN review_prescribedburn  pb ON ((p.id = pb.prescription_id)))
				 LEFT JOIN review_acknowledgement ack ON ((pb.id = ack.burn_id)))
				 LEFT JOIN review_burnprogramlink link ON ((p.id = link.prescription_id)))
			WHERE (
				(((ack.acknow_type)::text = 'SDO_A'::text) AND (pb.form_name = 1)) OR -- approved 268a
				((((ack.acknow_type)::text = 'SDO_B'::text) AND (pb.form_name = 2)) AND (pb.status = 1))) -- approved active 268b
			group by
				p.id,p.burn_id, pb.location, p.forest_blocks, burn_target_date, indicative_area,
				burn_target_long, burn_target_lat, burn_est_start, link.wkb_geometry,
				burn_planned_area_today, burn_planned_distance_today, burn_target_date_raw
			ORDER BY p.burn_id, burn_target_date_raw;
			create or replace view review_v_todaysburns as select * from review_v_dailyburns where burn_target_date_raw = current_date;
			create or replace view review_v_yesterdaysburns as select * from review_v_dailyburns where burn_target_date_raw = current_date - interval '1 day';
                        CREATE  OR REPLACE  FUNCTION review_f_lastdaysburns() RETURNS setof review_v_dailyburns AS $$
                        DECLARE
                            last_date review_v_dailyburns.burn_target_date_raw%TYPE;
                        BEGIN
                            SELECT max(pb.date) INTO last_date
                            FROM
                                review_prescribedburn  pb LEFT JOIN review_acknowledgement ack ON pb.id = ack.burn_id
                            WHERE (
                                    (((ack.acknow_type)::text = 'SDO_A'::text) AND (pb.form_name = 1))
                                    OR
                                    ((((ack.acknow_type)::text = 'SDO_B'::text) AND (pb.form_name = 2)) AND (pb.status = 1))
                                   )
                                   AND (pb.date < current_date);
                        
                            IF last_date IS NULL THEN
                                RETURN QUERY SELECT * FROM review_v_dailyburns WHERE false;
                            ELSE
                                RETURN QUERY SELECT * FROM review_v_dailyburns WHERE burn_target_date_raw = last_date;
                            END IF;
                        END;
                        $$ LANGUAGE plpgsql;
			create or replace view review_v_lastdaysburns as select * from review_f_lastdaysburns();

                        ''')
