import logging
import os
from datetime import timedelta,datetime
from dateutil import tz
from decimal import Decimal

from django.contrib.gis.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save,m2m_changed
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q, Max, Sum
from django.forms import ValidationError
from django.template.defaultfilters import truncatewords
from django.utils.safestring import mark_safe
from django.utils import timezone

from dpaw_utils.models import AuditMixin,DictMixin,SelectOptionMixin

from pbs.risk.models import (Register, Risk, Action, Complexity, Context, Treatment)

logger = logging.getLogger("log." + __name__)

# Create your models here.
class Season(AuditMixin):
    #SEASON_SPRING = 1
    #SEASON_SUMMER = 2
    #SEASON_AUTUMN = 3
    #SEASON_WINTER = 4
    #SEASON_EARLY_DRY = 5
    #SEASON_LATE_DRY = 6
    #SEASON_WET = 7
    SEASON_ANNUAL = 8
    SEASON_CHOICES = (
        #(SEASON_SUMMER, "Summer"),
        #(SEASON_AUTUMN, "Autumn"),
        #(SEASON_WINTER, "Winter"),
        #(SEASON_SPRING, "Spring"),
        #(SEASON_EARLY_DRY, "Early Dry"),
        #(SEASON_LATE_DRY, "Late Dry"),
        #(SEASON_WET, "Wet"),
        (SEASON_ANNUAL, "Annual"),
    )

    name = models.PositiveSmallIntegerField(
        choices=SEASON_CHOICES, default=SEASON_ANNUAL)
    start = models.DateField(help_text="Start date of season")
    end = models.DateField(help_text="End date of season")

    def __str__(self):
        if self.start.year == self.end.year:
            year = self.start.year
        else:
            year = "%s/%s" % (self.start.year, self.end.year)
        return "%s %s" % (self.get_name_display(), year)

    class Meta:
        ordering = ["-start"]


class RegionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Region(SelectOptionMixin,models.Model):
    """
    """
    name = models.CharField(max_length=64, unique=True)
    objects = RegionManager()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name


class DistrictManager(models.Manager):
    def current(self):
        # Filter queryset to return non-archived objects.
        return self.filter(archive_date__isnull=True)

    def archived(self):
        # Filter queryset to return archived objects only.
        return self.filter(archive_date__isnull=False)

    def get_by_natural_key(self, region, name):
        region = Region.objects.get_by_natural_key(region)
        return self.get(name=name, region=region)

class District(SelectOptionMixin,models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=3)
    archive_date = models.DateField(
        null=True, blank=True, help_text="Archive this District (prevent from creating new ePFPs)")
    objects = DistrictManager()

    def natural_key(self):
        return self.region.natural_key() + (self.name,)
    natural_key.dependencies = ['prescription.region']

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ShireManager(models.Manager):
    def get_by_natural_key(self, region, district, name):
        district = District.objects.get_by_natural_key(region, district)
        return self.get(name=name, district=district)

class Shire(models.Model):
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    objects = ShireManager()

    def natural_key(self):
        return self.district.natural_key() + (self.name,)
    natural_key.dependencies = ['prescription.district']

    def __str__(self):
        return "{0} ({1})".format(self.name, self.district)

    @property
    def shire_name(self):
        return str("{0} ({1})".format(str(self.name).split(',')[0], self.district))

    class Meta:
        ordering = ['name']
        unique_together = ('name', 'district')

class FuelType(models.Model):
    """
    Note that this model type is now referred to as "fuel type" in
    forms and views.
    TODO: rename the model.
    """
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Tenure(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Purpose(models.Model):
    name = models.CharField(max_length=200)
    display_order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

class ForecastArea(models.Model):
    districts = models.ManyToManyField(District)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class EndorsingRoleManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class EndorsingRole(models.Model):
    name = models.CharField(max_length=320)
    index = models.PositiveSmallIntegerField()
    disclaimer = models.TextField()
    archived = models.BooleanField(default=False, verbose_name="Role archived?")

    objects = EndorsingRoleManager()

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['index']

class RegionalObjective(AuditMixin):
    """
    """
    IMPACT_REGION = 1
    IMPACT_FMA = 2
    IMPACT_CHOICES = (
        (IMPACT_REGION, 'Region'),
        (IMPACT_FMA, 'Fire Management Area')
    )
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    impact = models.PositiveSmallIntegerField(
        choices=IMPACT_CHOICES, default=IMPACT_REGION,
        help_text="Area of application for objective",
        verbose_name="scale of application")
    fma_names = models.TextField(
        help_text="If the impact of this objective is Fire Management Area, "
                  "enter the names of the areas of application here",
        verbose_name="Fire Management Areas", blank=True)
    objectives = models.TextField()

    def __str__(self):
        return self.objectives[:64]

    class Meta:
        verbose_name = 'Regional Fire Management Plan Objective'
        verbose_name_plural = 'Regional Fire Management Plan Objectives'

class SMEAC(models.Model):
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.category

class DefaultBriefingChecklist(models.Model):
    smeac = models.ForeignKey(SMEAC, verbose_name="SMEACS", on_delete=models.PROTECT)
    title = models.CharField(max_length=200)

class Prescription(DictMixin,AuditMixin):
    """
    A Prescription is the core object in the system. It should contain all the
    top level attributes imported from Prescription Program Planning except
    Purposes and Objectives.
    """
    PRIORITY_UNSET = 0
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    PRIORITY_NOT_APPLICABLE = 4

    PRIORITY_CHOICES = (
        (PRIORITY_UNSET, 'Unset'),
        (PRIORITY_LOW, '1'),
        (PRIORITY_MEDIUM, '2'),
        (PRIORITY_HIGH, '3')
    )

    SENSING_PRIORITY_CHOICES = (
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_NOT_APPLICABLE, 'Not Applicable'),
    )

    # # TODO: Remove when PBS-1551 is closed
    # ALLOCATION_CHOICES = (
    #       (42, '42 - Native forest'),
    #       (43, '43 - Plantations'),
    #       (72, '72 - Prescribed fire'),
    #       (7204, '72-04 - Recoupable projects'),
    # )

    PLANNING_DRAFT = 1
    PLANNING_SUBMITTED = 2
    PLANNING_APPROVED = 3
    PLANNING_CHOICES = (
        (PLANNING_DRAFT, 'Draft'),
        (PLANNING_SUBMITTED, 'Seeking Corporate Approval'),
        (PLANNING_APPROVED, 'Corporate Approved'),
    )

    ENDORSEMENT_DRAFT = 1
    ENDORSEMENT_SUBMITTED = 2
    ENDORSEMENT_APPROVED = 3
    ENDORSEMENT_CHOICES = (
        (ENDORSEMENT_DRAFT, 'Not Endorsed'),
        (ENDORSEMENT_SUBMITTED, 'Seeking Endorsement'),
        (ENDORSEMENT_APPROVED, 'Endorsed'),
    )

    APPROVAL_DRAFT = 1
    APPROVAL_SUBMITTED = 2
    APPROVAL_APPROVED = 3
    APPROVAL_CHOICES = (
        (APPROVAL_DRAFT, 'Not Approved'),
        (APPROVAL_SUBMITTED, 'Seeking Approval'),
        (APPROVAL_APPROVED, 'Approved'),
    )

    IGNITION_NOT_STARTED = 1
    IGNITION_COMMENCED = 2
    IGNITION_COMPLETE = 3
    IGNITION_STATUS_CHOICES = (
        (IGNITION_NOT_STARTED, 'No Ignitions'),
        (IGNITION_COMMENCED, 'Ignition Commenced'),
        (IGNITION_COMPLETE, 'Ignition Completed'),
    )

    STATUS_OPEN = 1
    STATUS_CLOSED = 2
    STATUS_CHOICES = (
        (STATUS_OPEN, 'Burn Open'),
        (STATUS_CLOSED, 'Burn Closed'),
    )

    YES_NO_NULL_CHOICES = (
        (None, '-----'),
        (False, 'No'),
        (True, 'Yes'),
    )

    INT_CHOICES = [(i, i) for i in range(1, 100)]

    today = timezone.now().date()
    fin_year =  today.year if today.month <= 6 else today.year + 1
    yr1 = str(fin_year - 1) + '/' + str(fin_year)
    yr2 = str(fin_year)     + '/' + str(fin_year + 1)
    yr3 = str(fin_year + 1) + '/' + str(fin_year + 2)
    yr4 = str(fin_year + 2) + '/' + str(fin_year + 3)
    FNCL_YEAR_CHOICES = [
        [yr1, yr1],
        [yr2, yr2],
        [yr3, yr3],
        [yr4, yr4],
    ]

    prev_yr1 = str(fin_year - 2) + '/' + str(fin_year - 1)
    prev_yr2 = str(fin_year - 3) + '/' + str(fin_year - 2)
    prev_yr3 = str(fin_year - 4) + '/' + str(fin_year - 3)
    prev_yr4 = str(fin_year - 5) + '/' + str(fin_year - 4)
    LAST_FNCL_YEAR_CHOICES = [
        [prev_yr1, prev_yr1],
        [prev_yr2, prev_yr2],
        [prev_yr3, prev_yr3],
        [prev_yr4, prev_yr4],
    ]

    burn_id = models.CharField(max_length=7, verbose_name="Burn ID")
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    district = models.ForeignKey(District, blank=True, null=True, on_delete=models.PROTECT)
    shires = models.ManyToManyField(Shire, blank=True)
    planned_year = models.PositiveIntegerField(
        verbose_name="Planned Year", blank=True)
    financial_year = models.CharField(max_length=10, verbose_name="Financial Year",
        default=yr1)
    planned_season = models.PositiveSmallIntegerField(
        verbose_name="Planned Season", default=Season.SEASON_ANNUAL,
        blank=True, null=True)
    last_year = models.CharField(
        verbose_name="Year Last Burnt", max_length=64, blank=True, null=True)
    last_season = models.CharField(
        max_length=64, verbose_name="Season Last Burnt", blank=True, null=True)
    last_season_unknown = models.BooleanField(
        default=False, verbose_name="Last Season Unknown?")
    last_year_unknown = models.BooleanField(
        default=False, verbose_name="Last Year Unknown?")
    contentious = models.NullBooleanField(
        choices=YES_NO_NULL_CHOICES,
        default=None, help_text="Is this burn contentious?")
    contentious_rationale = models.TextField(
        help_text="If this burn is contentious, a short explanation of why",
        verbose_name="Rationale", null=True, blank=True)
    aircraft_burn = models.BooleanField(
        verbose_name="Aircraft Burn?", default=False,
        help_text="Does this burn involve aerial ignition?")
    # # TODO: Remove when PBS-1551 is closed
    # allocation = models.PositiveSmallIntegerField(
    #     max_length=64, choices=ALLOCATION_CHOICES,
    #     verbose_name="Program Allocation", blank=True, null=True,
    #     help_text="Program code which is assigned to the burn")
    priority = models.PositiveSmallIntegerField(
        verbose_name="Overall Priority", help_text="Priority for this burn",
        choices=PRIORITY_CHOICES, default=PRIORITY_UNSET)
    rationale = models.TextField(
        verbose_name="Overall Rationale", blank=True, null=True)
    remote_sensing_priority = models.PositiveSmallIntegerField(
        choices=SENSING_PRIORITY_CHOICES, default=PRIORITY_NOT_APPLICABLE,
        verbose_name=mark_safe("Remote Sensing Priority"),
        help_text=("Remote sensing priority"))
    treatment_percentage = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(100)], blank=True, null=True,
        help_text="Percentage of the planned area that will be treated (%)")
    location = models.CharField(
        help_text="Example: Nollajup Nature Reserve - 8.5 KM S of Boyup Brook",
        max_length=320, blank=True, null=True)
    area = models.DecimalField(
        verbose_name="Planned Burn Area", max_digits=12, decimal_places=1,
        help_text="Planned burn area (in ha)",
        validators=[MinValueValidator(0)], default=0.0)
    perimeter = models.DecimalField(
        max_digits=12, decimal_places=1,
        help_text="Planned burn perimeter (in km)",
        validators=[MinValueValidator(0)], default=0.0)
    regional_objectives = models.ManyToManyField(
        'RegionalObjective', help_text="Regional Objectives",
        verbose_name="Regional Objectives", blank=True)
    fuel_types = models.ManyToManyField(
        FuelType, verbose_name="Fuel Types",  blank=True)
    tenures = models.ManyToManyField(Tenure, blank=True)
    bushfire_act_zone = models.TextField(
        verbose_name="Bushfires Act Zone", null=True)
    prohibited_period = models.TextField(
        verbose_name="Prohibited Period", blank=True, null=True)
    forecast_areas = models.ManyToManyField(
        ForecastArea, verbose_name="Forecast Areas", blank=True)
    prescribing_officer = models.ForeignKey(
        User, verbose_name="Prescribing Officer", blank=True, null=True, on_delete=models.PROTECT)
    closure_officer = models.ForeignKey(
        User, verbose_name="Closure Officer", blank=True, null=True, related_name='closure', on_delete=models.PROTECT)
    short_code = models.TextField(
        verbose_name="Short Code", blank=True, null=True)
    purposes = models.ManyToManyField(Purpose)
    planning_status = models.PositiveSmallIntegerField(
        verbose_name="Planning Status", choices=PLANNING_CHOICES,
        default=PLANNING_DRAFT)
    planning_status_modified = models.DateTimeField(
        verbose_name="Planning Status Modified", editable=False, null=True)
    endorsing_roles = models.ManyToManyField(
        EndorsingRole, verbose_name="Endorsing Roles")
    endorsing_roles_determined = models.BooleanField(
        verbose_name="Required Endorsing Roles", default=False)
    endorsement_status = models.PositiveSmallIntegerField(
        verbose_name="Endorsement Status", choices=ENDORSEMENT_CHOICES,
        default=ENDORSEMENT_DRAFT)
    endorsement_status_modified = models.DateTimeField(
        verbose_name="Endorsement Status Modified", editable=False, null=True)
    approval_status = models.PositiveSmallIntegerField(
        verbose_name="Approval Status", choices=APPROVAL_CHOICES,
        default=APPROVAL_DRAFT)
    approval_status_modified = models.DateTimeField(
        verbose_name="Approval Status Modified", editable=False, null=True)
    ignition_status = models.PositiveSmallIntegerField(
        verbose_name="Ignition Status",
        choices=IGNITION_STATUS_CHOICES, default=IGNITION_NOT_STARTED)
    ignition_status_modified = models.DateTimeField(
        verbose_name="Ignition Status Modified", editable=False, null=True)
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=STATUS_OPEN)
    status_modified = models.DateTimeField(
        verbose_name="Status Modified", editable=False, null=True)
    ignition_completed_date = models.DateField(
        blank=True, null=True, verbose_name="Ignition Completed")
    forest_blocks = models.TextField(
        verbose_name="Forest Blocks (if applicable)", blank=True)
    carried_over = models.BooleanField(editable=False, default=False)
    # Boolean field to indicated whether all associated Contingency models have
    # been migrated to the newer data structure.
    # Never meant to be manually edited, and should be updated by the
    # ModelAdmin save_model method.
    # Will probably be removed when all contigency objects have been migrated.
    contingencies_migrated = models.BooleanField(default=False, editable=False)
#    reviewed = models.BooleanField(verbose_name="Reviewed by FMSB and DRFMS", default=False, editable=False)

    @property
    def approval_expiry(self):
        if self.is_approved:
            return defaultfilters.date(self.current_approval.valid_to)
        else:
            return "Not applicable"

    
    @property
    def locations(self):
        if not hasattr(self,"_locations"):
            if not self.location:
                setattr(self,"_locations",None)
            elif self.location.startswith("Within the locality of"):
                setattr(self,"_locations",[self.location[len("Within the locality of"):].strip()])
            else:
                setattr(self,"_locations",[l.strip() for l in self.location.split('|')] if self.location else None)
        return self._locations
    @locations.setter
    def locations(self,value):
        self._locations = value
        if not self._locations:
            self.location = None
        elif isinstance(self._locations,(list,tuple)):
            if len(self._locations) == 1 or not any(self._locations[1:]):
                self.location = "Within the locality of {}".format(self._locations[0])
            else:
                self.location = "|".join(self._locations)
        else:
            self.location = "Within the locality of {}".format(self._locations)

    def _set_loc(self,index,value):
        locations = self.locations
        if value:
            value = value.strip()
        else:
            value = ""
        if locations and len(locations) > index:
            locations[index] = value
        else:
            if locations is None:
                locations = []
            
            if len(locations) < index:
                locations.extend([""] * (index - len(locations)))
                
            locations.append(value)

        self.locations = locations

    @property
    def loc_locality(self):
        return self.locations[0] if self.locations and len(self.locations) >= 1 else None
    @loc_locality.setter
    def loc_locality(self,value):
        self._set_loc(0,value)

    @property
    def loc_distance(self):
        return self.locations[1] if self.locations and len(self.locations) >= 2 else None
    @loc_distance.setter
    def loc_distance(self,value):
        self._set_loc(1,value)

    @property
    def loc_direction(self):
        return self.locations[2] if self.locations and len(self.locations) >= 3 else None
    @loc_direction.setter
    def loc_direction(self,value):
        self._set_loc(2,value)

    @property
    def loc_town(self):
        return self.locations[3] if self.locations and len(self.locations) >= 4 else None
    @loc_town.setter
    def loc_town(self,value):
        self._set_loc(3,value)


    @property
    def is_reviewed(self):
        if all(self.burnstate.filter(review_type=x).exists() for x in ['FMSB','DRFMS']):
            return True
        else:
            return False

    @property
    def allocations(self):
        """Return a display tag of program funding allocations"""
        fas = list(FundingAllocation.objects.filter(prescription=self, proportion__gt=0))
        if not fas:
            return None
        alloc = ", ".join(["{} ({:.1f}%)".format(fa.allocation, fa.proportion) for fa in fas])
        return alloc

    @property
    def uploaded_documents_total_size(self):
        """
        Returns the total size of uploaded documents in MB
        """
        total_size = 0
        try:
            if len(self.document_set.all()) > 0:
                for doc in self.document_set.all():
                    if os.path.exists(doc.document.path):
                        total_size += doc.document.size
                return round(total_size/1024/1024., 2)
        except ValueError:
            pass
        return 0.0

    @property
    def uploaded_documents(self):
        """
        Returns the name and size (MB) of uploaded documents
        """
        try:
            if len(self.document_set.all()) > 0:
                return [ (d.document.name, round(d.document.size/1024/1024., 2))
                         for d in self.document_set.all()
                         if os.path.exists(d.document.path) ]
        except ValueError:
            pass
        return []

    @property
    def shire_str(self):
        return str(', '.join(x.shire_name for x in self.shires.all()))

    @property
    def treatments(self):
        return Treatment.objects.filter(register__prescription=self)

    # template tag or not needed :)
    @property
    def document_json(self):
        from pbs.document.models import DocumentCategory
        documents = OrderedDict()
        for cat in DocumentCategory.objects.all().order_by('order'):
            docs = []
            for item in self.document_set.filter(category=cat):
                docs.append(item.document.name.split("/")[-1])
            documents[cat.name] = docs
        return documents

    @property
    def evaluations(self):
        from pbs.report.models import Evaluation
        return Evaluation.objects.filter(criteria__prescription=self)

    @property
    def pre_burn_actions(self):
        return Action.objects.filter(risk__prescription=self, pre_burn=True)

    @property
    def pre_burn_modified(self):
        actions = self.pre_burn_actions
        if len(actions) == 0:
            return None
        modified_old = actions[0].modified
        for action in actions:
            modified_new = action.modified
            if modified_new > modified_old:
                modified_old = modified_new
        return modified_old

    @property
    def day_of_burn_actions(self):
        return Action.objects.filter(risk__prescription=self, day_of_burn=True)

    @property
    def day_of_burn_modified(self):
        actions = self.day_of_burn_actions
        if len(actions) == 0:
            return None
        modified_old = actions[0].modified
        for action in actions:
            modified_new = action.modified
            if modified_new > modified_old:
                modified_old = modified_new
        return modified_old

    @property
    def post_burn_actions(self):
        return Action.objects.filter(risk__prescription=self, post_burn=True)

    @property
    def post_burn_modified(self):
        actions = self.post_burn_actions
        if len(actions) == 0:
            return None
        modified_old = actions[0].modified
        for action in actions:
            modified_new = action.modified
            if modified_new > modified_old:
                modified_old = modified_new
        return modified_old

    @property
    def briefing_checklist_modified(self):
        briefing_checklist = BriefingChecklist.objects.filter(prescription=self)
        if len(briefing_checklist) == 0:
            return None
        modified_old = briefing_checklist[0].modified
        for action in briefing_checklist:
            modified_new = action.modified
            if modified_new > modified_old:
                modified_old = modified_new
        return modified_old

    # The field or widget should be able to give us this value.
    # Possible refactor
    @property
    def location_text(self):
        if self.location:
            value = self.location.split('|')
            if len(value) > 1:
                return '{0} - {1}km(s) {2} of {3}'.format(
                    value[0] or '', (value[1] or ''), (value[2] or ''),
                    (value[3] or ''))
            else:
                return self.location
        return ''

    @property
    def season(self):
        return "%s" % (self.financial_year)

    @property
    def last_year_burnt(self):
        if self.last_year_unknown:
            return "Unknown"
        else:
            return str(self.last_year)

    @property
    def last_season_burnt(self):
        if self.last_season_unknown:
            return "Unknown"
        else:
            return self.last_season

    @property
    def planned_season_object(self):
        """
        Try to retrieve the planned season object based on this prescription's
        year and season. If for any reason the query fails (Season not found,
        no planned year, no planned season) return None.
        """
        try:
            return Season.objects.get(name=self.planned_season,
                                      start__year=self.planned_year)
        except:
            pass

    @property
    def is_draft(self):
        """
        Return true if this ePFP is in draft status.
        """
        return self.endorsement_status == self.ENDORSEMENT_DRAFT

    @property
    def is_endorsed(self):
        """
        Return true if this ePFP has been fully endorsed.
        """
        return self.endorsement_status == self.ENDORSEMENT_APPROVED

    @property
    def is_planned(self):
        """
        Return true if this ePFP has received planning approval from corporate
        executive.
        """
        return self.planning_status == self.PLANNING_APPROVED

    @property
    def has_corporate_approval(self):
        return self.planning_status == self.PLANNING_APPROVED

    @property
    def is_approved(self):
        """
        Return true if this ePFP has been approved.
        """
        return self.approval_status == self.APPROVAL_APPROVED

    @property
    def is_closed(self):
        return self.status == self.STATUS_CLOSED

    @property
    def is_burnt(self):
        return self.ignition_status == self.IGNITION_COMPLETE

    @property
    def has_ignitions(self):
        return self.ignition_status != self.IGNITION_NOT_STARTED

    @property
    def ignition_commenced(self):
        return self.areaachievement_set.earliest()

    @property
    def current_approval(self):
        """
        This is the __str__ method returned by the approval.latest()

        def __str__(self):
            return "Approved by {0} until {1}".format(
                self.creator.get_full_name(), self.valid_to.strftime('%d/%b/%Y'))
        """
        return self.approval_set.latest()

    @property
    def current_approval_approver(self):
        return self.current_approval.creator.get_full_name()

    @property
    def current_approval_valid_period(self):
        return self.current_approval.valid_to.strftime('%d/%b/%Y')

    @property
    def carried_season(self):
        if self.carried_over:
            season = self.carried_over_from_season
            year = self.carried_over_from_year
            return Season.objects.get(name=season, start__year=year)
        else:
            return None

    @property
    def can_corporate_approve(self):
        """
        Return true if this prescription can be submitted for corporate
        approval.
        """
        return (
            self.priority != Prescription.PRIORITY_UNSET and
            self.area != Decimal('0.0') and
            self.perimeter != Decimal('0.0') and
            (self.location is not None and self.location != '') and
            (self.treatment_percentage != 0 and self.treatment_percentage is not None) and
            self.purposes.count() != 0 and
            (sum(fa.proportion for fa in FundingAllocation.objects.filter(prescription=self)) == Decimal('100.0')) and
            # self.purposes.count() != 0 and self.allocation is not None and
            (self.last_season is not None or self.last_season_unknown) and
            (self.last_year is not None or self.last_year_unknown) and
            self.contentious is not None
        )

    @property
    def can_endorse(self):
        """
        Return true if this prescription can be submitted for endorsement.
        """
        return (self.planning_status == self.PLANNING_APPROVED and
                self.pre_state.finished and self.day_state.finished and
                self.endorsing_roles_determined)

    @property
    def can_edit_risk_register(self):
        """
        Return true if all of part A is complete (except Risk Register), all of
        part B, and post-burn actions of part C.
        Refer to BR-14.
        """
        return (self.pre_state.complete_except_risk and self.day_state.finished
                and self.post_state.post_actions)

    @property
    def can_select_endorsing_roles(self):
        """
        Return true if endorsing roles can be selected for this prescription.
        """
        return (self.is_draft and self.pre_state.complexity_analysis and
                self.pre_state.risk_register)

    @property
    def all_endorsed(self):
        """
        Determine if all needed endorsements have been endorsed.
        """
        return (self.endorsement_set.filter(endorsed=True).count() ==
                self.endorsing_roles.count())

    @property
    def not_endorsed_endorsing_roles(self):
        # we take endoring roles for this prescription and exclude the ones
        # that has been endorsed
        return self.endorsing_roles.exclude(
            id__in=self.endorsement_set.values_list('role__id', flat=True))

    @property
    def all_reviewed(self):
        """
        Determine if all needed endorsements have been reviewed.
        """
        return self.not_endorsed_endorsing_roles.count() == 0

    @property
    def can_approve(self):
        """
        Return true if this prescription can be submitted for approval.
        """
        return (self.can_endorse and
                self.endorsement_status == self.ENDORSEMENT_APPROVED)

    @property
    def can_epfp_approve(self):
        """
        Return true if this prescription can be submitted for epfp approval
        or extension.
        """

        return ((self.get_maximum_risk.final_risk_level !=
                 self.get_maximum_risk.LEVEL_VERY_HIGH) and
                # draft
                (self.can_approve and
                 self.approval_status == self.APPROVAL_DRAFT) or
                # submitted
                self.approval_status == self.APPROVAL_SUBMITTED or
                # extension
                (self.approval_status == self.APPROVAL_APPROVED and
                 self.current_approval and
                 self.current_approval.extension_count < 3))

    @property
    def can_ignite(self):
        """
        Return true if this burn plan can be acted upon and ignited.
        """
        return self.pre_state.finished and self.day_state.finished

    @property
    def can_close(self):
        """
        Return true if this burn plan can be closed.
        Refer to BR-50.
        """
        return (self.pre_state.finished and self.day_state.finished and
                self.post_state.post_burn_checklist and
                self.ignition_completed_date)

    @property
    def get_maximum_draft_risk(self):
        registers = self.register_set.annotate(Max('draft_risk_level'))
        if registers.count() > 0:
            return registers.latest('draft_risk_level__max')
        else:
            return None

    @property
    def maximum_draft_risk(self):
        """
        Determine the maximum draft risk of this burn plan.
        """
        register = self.get_maximum_draft_risk
        if register:
            return register.draft_risk_level
        else:
            return Register.LEVEL_VERY_HIGH

    @property
    def get_maximum_risk(self):
        registers = self.register_set.annotate(Max('final_risk_level'))
        if registers.count() > 0:
            return registers.latest('final_risk_level__max')
        else:
            return None

    @property
    def maximum_risk(self):
        """
        Determine the maximum risk of this burn plan.
        """
        register = self.get_maximum_risk
        if register:
            return register.final_risk_level
        else:
            return Register.LEVEL_VERY_HIGH

    @property
    def get_maximum_complexity(self):
        return self.complexity_set.latest('rating')

    @property
    def maximum_complexity(self):
        """
        Determine the maximum complexity of this burn plan.
        """
        return self.get_maximum_complexity.rating

    @property
    def total_edging_depth(self):
        from pbs.report.models import AreaAchievement
        return AreaAchievement.objects.filter(prescription=self).aggregate(Sum('edging_depth_estimate'))['edging_depth_estimate__sum']

    @property
    def total_edging_length(self):
        from pbs.report.models import AreaAchievement
        return AreaAchievement.objects.filter(prescription=self).aggregate(Sum('edging_length'))['edging_length__sum']

    @property
    def total_burnt_area_estimate(self):
        from pbs.report.models import AreaAchievement
        return AreaAchievement.objects.filter(prescription=self).aggregate(Sum('area_estimate'))['area_estimate__sum']

    @property
    def total_burnt_area_estimate_modified(self):
        from pbs.report.models import AreaAchievement
        return AreaAchievement.objects.filter(prescription=self).aggregate(Max('modified'))["modified__max"]

    @property
    def total_treatment_area(self):
        from pbs.report.models import AreaAchievement
        return AreaAchievement.objects.filter(prescription=self).aggregate(Sum('area_treated'))['area_treated__sum']

    @property
    def complexities(self):
        qs = self.complexity_set.all()
        qs.modified = qs.aggregate(Max('modified'))["modified__max"]
        return qs

    @property
    def contingencies(self):
        qs = self.contingency_set.all()
        qs.modified = qs.aggregate(Max('modified'))["modified__max"]
        return qs

    @property
    def priorities(self):
        # Relevant priorities
        qs = self.priorityjustification_set.filter(relevant=True)
        qs.modified = qs.aggregate(Max('modified'))["modified__max"]
        return qs

    @property
    def ways(self):
        if not hasattr(self, '_all_ways'):
            roads = RoadSegment.objects.filter(prescription=self)
            trails = TrailSegment.objects.filter(prescription=self)
            ways = Way.objects.filter(prescription=self)
            inspections = SignInspection.objects.filter(way__prescription=self)
            traffic_diagrams = TrafficControlDiagram.objects.filter(roadsegment__prescription=self).exclude(name="custom").distinct()
        
            for qs in [roads, trails, ways, inspections]:
                qs.modified = qs.aggregate(Max('modified'))["modified__max"]
        
            self._all_ways = {
                "roads": roads,
                "trails": trails,
                "ways": ways,
                "standard_traffic_diagrams": traffic_diagrams,
                "inspections": inspections,
                "modified": max([modified for modified in
                                 (roads.modified, trails.modified,
                                 ways.modified, inspections.modified,
                                 current.created)
                                 if modified is not None])
            }

        return self._all_ways

    @property
    def risk_registers(self):
        # Relevant Risk Register's
        qs = Register.objects.filter(prescription=self)
        qs.modified = qs.aggregate(Max('modified'))["modified__max"]
        return qs

    @property
    def sectiona2_modified(self):
        # avoid circular import
        from pbs.stakeholder.models import CriticalStakeholder
        critical_stakeholders_modified = CriticalStakeholder.objects.filter(
            prescription=self).aggregate(Max('modified'))["modified__max"]
        context_map_modified = self.document_set.tag_names(
            "Context Map").aggregate(Max('modified'))["modified__max"]
        return max([modified for modified in
                    (self.priorities.modified, self.context_statements.modified,
                    critical_stakeholders_modified, context_map_modified,
                    self.created)
                    if modified is not None])

    @property
    def sectiona3_modified(self):
        objectives_modified = self.objective_set.aggregate(
            Max('modified'))["modified__max"]
        successcriteria_modified = self.successcriteria_set.aggregate(
            Max('modified'))["modified__max"]
        return max([modified for modified in
                    (objectives_modified, successcriteria_modified,
                    self.created)
                    if modified is not None])

    @property
    def sectionb5_modified(self):
        bp_modified = self.burningprescription_set.aggregate(
            Max('modified'))["modified__max"]
        ep_modified = self.edgingplan_set.aggregate(
            Max('modified'))["modified__max"]
        ls_modified = self.lightingsequence_set.aggregate(
            Max('modified'))["modified__max"]
        ea_modified = self.exclusionarea_set.aggregate(
            Max('modified'))["modified__max"]
        return max([modified for modified in
                    (bp_modified, ep_modified,
                    ls_modified, ea_modified,
                    self.created)
                    if modified is not None])

    @property
    def current_fmsb_record(self):
        return self.burnstate.filter(review_type='FMSB',review_date__gte=self.approval_set.latest().created)

    @property
    def current_drfms_record(self):
        return self.burnstate.filter(review_type='DRFMS',review_date__gte=self.approval_set.latest().created)

    @property
    def fmsb_record(self):
        return self.burnstate.filter(review_type='FMSB')

    @property
    def drfms_record(self):
        return self.burnstate.filter(review_type='DRFMS')

    @property
    def fmsb_group(self):
        return Group.objects.get(name='Fire Management Services Branch')

    @property
    def drfms_group(self):
        return Group.objects.get(name='Director Fire and Regional Services')

    def get_absolute_url(self):
        return "prescription/prescription/{}/".format(self.id)

    # Should have a template filter that does this already?
    def date_modified_local(self):
        local_zone = tz.tzlocal()
        return self.modified.astimezone(local_zone).strftime('%d/%m/%Y %H:%M:%S')

    def clear_endorsements(self, commit=True):
        self.endorsement_set.all().delete()
        self.endorsement_status = self.ENDORSEMENT_DRAFT
        if commit:
            self.save()

    def clear_approvals(self):
        # cancel endorsements and approvals
        self.clear_endorsements(commit=False)
        self.approval_set.all().delete()
        self.approval_status = self.APPROVAL_DRAFT
        self.save()
        # clear Section A/B/C complete flag(s) - set to false
        # Section A
        pre_state = self.pre_state
        pre_state.summary = False       # A1 - Burn Summary and Approval
        pre_state.save()

    def purposes_list(self):
        """
        Place 'Bushfire Risk Management' at top of list/string
        """
        #return ', '.join([i.name.strip('Management') for i in self.purposes.all()])
        purposes = [i.name for i in self.purposes.all()]
        if 'Bushfire Risk Management' in purposes:
            return 'Bushfire Risk Management, ' + ', '.join([i for i in purposes if i != 'Bushfire Risk Management'])
        return ', '.join([i for i in purposes])


    def clean_location(self):
        if ((self.location and
             len(self.location.split("Within the locality of ")))) == 1:
            location = self.location.split('|')
            if not (location[0] and location[1] and location[2] and
                    location[3]):
                raise ValidationError("You must enter/select a value in all "
                                      "fields. Alternatively, if entering "
                                      "only a locality, location will be "
                                      "stored as 'Within the locality of "
                                      "____'.")

    def clean_bushfire_act_zone(self):
        if self.bushfire_act_zone is None:
            raise ValidationError("You must enter the Bushfire Act Zone.")

    def clean(self):
        """
        if ((self.last_year and self.last_season and
             self.planned_year and self.planned_season and
             self.planned_year < self.last_year)):
            raise ValidationError("Last burnt season and year must be before "
                                  "planned burn season and year.")
        """

        if self.last_year and self.last_year_unknown:
            raise ValidationError("Last year can not be set and marked "
                                  "unknown at the same time.")

        if self.last_season and self.last_season_unknown:
            raise ValidationError("Last season can not be set and marked "
                                  "unknown at the same time.")

    def save(self, **kwargs):
        """
        Calculate the burn id on every save. This is based on the algorithm
        described in PBS-1258.
        """
        # Get all open burn ids and loop through them until we find one that
        # is available. If we can't find an available number, take the number
        # one higher than the last burn id.
        #import pudb; pudb.set_trace()
        if not self.pk:
            try:
                prescription = Prescription.objects.filter(
                    district=self.district).latest('burn_id')
            except Prescription.DoesNotExist as es:
                prescription = None

            # Don't recycle values because its a really bad idea.
            if prescription is None:
                burn_id = 1
            else:
                burn_id = int(prescription.burn_id.split('_')[1])

            self.burn_id = "%s_%03d" % (self.district.code, burn_id)

        # Update ignition status to complete if ignition_completed_date
        if self.ignition_completed_date:
            self.ignition_status = self.IGNITION_COMPLETE
            self.ignition_status_modified = timezone.now()
        else:
            if self.areaachievement_set.all().count() > 0:
                self.ignition_status = self.IGNITION_COMMENCED
                self.ignition_status_modified = timezone.now()
                self.ignition_status = self.IGNITION_NOT_STARTED
                self.ignition_status_modified = timezone.now()

        # Check the actions_migrated and notifications_migrated fields
        # for all child Contingency objects.
        # If both are True, mark the contingencies_migrated field as True
        # otherwise mark it False.
        for c in self.contingencies.all():
            if c.actions_migrated and c.notifications_migrated:
                self.contingencies_migrated = True
            else:
                self.contingencies_migrated = False

        # for consistency - migration from year to financial_year
        if self.financial_year:
            self.planned_year = int(self.financial_year.split('/')[0])

        # because tenures and vegetation may have changed
        self.description = self.generate_description()

#        if all(x in [i.review_type for i in self.burnstate.all()] for x in ['FMSB','DRFMS']):
#            self.reviewed = True
#        else:
#            self.reviewed = False

        super(Prescription, self).save(**kwargs)

    def generate_description(self):
        try:
            if self.tenures.count() > 0:
                tenure_names = [tenure.name for tenure in self.tenures.all()]
                if len(tenure_names) > 1:
                    located  = ', '.join(tenure_names[:-1]) + ' and ' + tenure_names[-1]
                else:
                    located  = ', '.join(tenure_names)

            else:
                located = "TBD"
        except ValueError as e:
            located = "TBD"

        if self.last_year_unknown:
            last_burnt = "is unknown"
        else:
            last_burnt = "was %s" % self.last_year

        blocks = " in %s" % self.forest_blocks if self.forest_blocks else ""

        try:
            if self.fuel_types.count() > 0:
                veg_type_names = [v.name for v in self.fuel_types.all()]

                if len(veg_type_names) > 1:
                    veg_types  = ', '.join(veg_type_names[:-1]) + ' and ' + veg_type_names[-1]
                else:
                    veg_types  = ', '.join(veg_type_names)

            else:
                veg_types = "TBD"
        except ValueError as e:
            veg_types = "TBD"

        return (
            "Prescribed burn %(burn_id)s is located in %(located)s, "
            "%(location_text)s%(forest_blocks)s. The area of the burn is "
            "approximately %(area).1f hectares and consists primarily of "
            "%(veg_types)s. Year last burnt %(last_burnt)s."
        ) % {
            'located': located,
            'location_text': self.location_text or "TBD",
            'forest_blocks': blocks,
            'veg_types': veg_types,
            'last_burnt': last_burnt,
            'burn_id': self.burn_id,
            'area': self.area,
        }

    def __str__(self):
        return self.burn_id

    class Meta:
        verbose_name = 'Prescribed Fire Plan'
        verbose_name_plural = 'Prescribed Fire Plans'
        permissions = (
            ("can_corporate_approve", "Can apply corporate approval"),
            ("can_delete_approval", "Can remove ePFP approval"),
            ("can_carry_over", "Can carry over burns"),
            ("can_admin", "Can admin burns"),
        )


class FundingAllocation(models.Model):
    """
    Allow multiple funding allocations for a Prescription.

    Feature PBS-1551

    Note that `proportion` is a value between 0 and 1.
    """
    ALLOCATION_CHOICES = (
        (42, '42 - Native forest'),
        (43, '43 - Plantations'),
        (72, '72 - Prescribed fire'),
        (7204, '72-04 - Recoupable projects'),
    )

    prescription = models.ForeignKey(Prescription, on_delete=models.PROTECT)
    allocation = models.PositiveSmallIntegerField(
        choices=ALLOCATION_CHOICES,
        verbose_name="Program",
        help_text="Program funding code which is assigned to the burn")
    proportion = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        verbose_name="Proportion of budget covered [%]",
        help_text="Percentage between 0 and 100")

    def clean(self):
        """Ensure the number is a percentage"""
        _min, _max = 0, 100
        if not _min <= self.proportion <= _max:
            raise ValidationError(
                "Percentage must be a decimal between 0 and 100")
        if self.allocation is None:
            raise ValidationError(
                "Allocation code must not be empty")

    def save(self, *args, **kwargs):
        """Validate before saving."""
        self.clean()
        # if self.id:  # Exisiting record
        #     # Get prescritpion as it doesn't roundtrip
        #     self.prescription = FundingAllocation.objects.get(pk=self.id).prescription
        # else: # We need a new allocation record with the current prescription
        #     pass
        super(FundingAllocation, self).save(*args, **kwargs)

    def __str__(self):
        name = "{}: {:5.2f}%".format(
            self.get_allocation_display(),
            self.proportion)
        return name

    class Meta:
        unique_together = ('prescription', 'allocation')

class Objective(AuditMixin):
    """
    """
    prescription = models.ForeignKey(
        Prescription, help_text="Prescription this objective belongs to", on_delete=models.PROTECT)
    objectives = models.TextField(help_text="Prescription Objectives")

    def __str__(self):
        return self.objectives

    class Meta:
        verbose_name = "Burn Objective"
        verbose_name_plural = "Burn Objectives"
        ordering = ["created"]

class SuccessCriteria(AuditMixin):
    """
    """
    prescription = models.ForeignKey(
        Prescription,
        help_text="Prescription this success criteria belongs to", on_delete=models.PROTECT)
    objectives = models.ManyToManyField(Objective)
    criteria = models.TextField(verbose_name="Success Criteria")


    def __str__(self):
        return self.criteria

    class Meta:
        verbose_name = "Success Criteria"
        verbose_name_plural = "Success Criterias"
        ordering = ["created"]

class BriefingChecklist(AuditMixin):
    prescription = models.ForeignKey(Prescription, on_delete=models.PROTECT)
    title = models.TextField(verbose_name="Topic")
    smeac = models.ForeignKey(SMEAC, verbose_name="SMEACS", on_delete=models.PROTECT)
    action = models.ForeignKey('risk.Action', blank=True, null=True, on_delete=models.PROTECT)
    notes = models.TextField(verbose_name="Briefing Notes", blank=True)

    def __str__(self):
        return '{0}|{1}'.format(self.smeac, truncatewords(self.title, 8))

    class Meta:
        verbose_name = "Checklist Item"
        verbose_name_plural = "Checklist Items"
        ordering = ['smeac__id', 'id']

class Endorsement(AuditMixin):
    ENDORSED_CHOICES = (
        (None, ''),
        (False, 'Reviewed and not endorsed'),
        (True, 'Endorsed'),
    )
    prescription = models.ForeignKey(Prescription, on_delete=models.PROTECT)
    role = models.ForeignKey(EndorsingRole, on_delete=models.PROTECT)
    endorsed = models.NullBooleanField(choices=ENDORSED_CHOICES, default=None)

    def __str__(self):
        if self.endorsed is not None:
            return "%s by %s" % (self.get_endorsed_display(),
                                 self.creator.get_full_name())
        else:
            return self.creator.get_full_name()

    class Meta:
        ordering = ['role']

class Approval(AuditMixin):
    prescription = models.ForeignKey(Prescription, on_delete=models.PROTECT)
    initial_valid_to = models.DateField(
        verbose_name="Valid To (Initial)",
        #default=timezone.now() + timezone.timedelta(days=365),
        editable=False)
    # the valid_to.default is redefined in the form to refer to the last day
    # of this prescription's planned season
    valid_to = models.DateField(verbose_name="Valid To")
    extension_count = models.PositiveSmallIntegerField(
        verbose_name="Extension Count", default=0,
        validators=[MaxValueValidator(3)], editable=False)

    @property
    def next_valid_to(self):
        return self.valid_to + timedelta(days=14)

    def clean_valid_to(self):
        """
        These were causing issues with WET season burns. They have been
        commented out for now.
        """
        #if ((self.valid_to and
        #     self.valid_to > self.prescription.planned_season_object.end)):
        #    raise ValidationError("A burn cannot be approved with a valid "
        #                          "date of later than the end of the planned "
        #                          "season.")
        #if ((self.valid_to and
        #     self.valid_to < self.prescription.planned_season_object.start)):
        #    raise ValidationError("A burn cannot be approved with a valid "
        #                          "date of earlier than the start of the "
        #                          "planned season.")

    def save(self, **kwargs):
        if not self.pk:
            self.initial_valid_to = self.valid_to
        super(Approval, self).save(**kwargs)

    def __str__(self):
        return "Approved by {0} until {1}".format(
            self.creator.get_full_name(), self.valid_to.strftime('%d/%b/%Y'))

    class Meta:
        ordering = ["-id"]
        get_latest_by = "valid_to"

class PriorityJustification(AuditMixin):
    PRIORITY_UNRATED = 0
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    PRIORITY_CHOICES = (
        (PRIORITY_UNRATED, 'Unrated'),
        (PRIORITY_LOW, '1'),
        (PRIORITY_MEDIUM, '2'),
        (PRIORITY_HIGH, '3'),
    )

    prescription = models.ForeignKey(Prescription, null=True, on_delete=models.PROTECT)
    purpose = models.ForeignKey(Purpose, verbose_name='Burn Purpose', on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField(default=0)
    criteria = models.TextField(
        verbose_name="Prioritisation Criteria", blank=True)
    rationale = models.TextField(blank=True)
    priority = models.PositiveSmallIntegerField(
        choices=PRIORITY_CHOICES, default=PRIORITY_UNRATED)
    relevant = models.BooleanField(default=False)

    def clean_rationale(self):
        if self.priority and not self.rationale:
            raise ValidationError('Rationale must be set for this purpose as '
                                  'it has been given a priority.')

    def clean_priority(self):
        if self.rationale and self.priority == 0:
            raise ValidationError('Priority must be set for this purpose as '
                                  'it has been given a rationale.')

    def __str__(self):
        return self.purpose.name

    class Meta:
        verbose_name = "Burn Priority Justification"
        verbose_name_plural = "Burn Priority Justifications"
        unique_together = ('purpose', 'prescription')
        ordering = ['order']


class PrescriptionListener(object):
    @staticmethod
    @receiver(post_save)
    def prescription_modified(sender, instance, created, **kwargs):
        if hasattr(instance, 'prescription'):
            prescription = instance.prescription
            if prescription is not None:
                prescription.save(update_fields=["modifier","modified"])     # update the modified and modifier fields


    @staticmethod
    @receiver(post_save, sender=Prescription)
    def create_risks(sender, instance, created, **kwargs):
        """
        For each standard risk, create a copy on the new prescription if the
        prescription has just been created.
        Also create complexities for this prescription.
        """
        from pbs.implementation.models import OperationalOverview
        if created:
            logger.debug("Creating standard risks for prescription %s" % instance)
            risks = []
            for risk in Risk.objects.filter(prescription=None, custom=False):
                risk.pk = None
                risk.prescription = instance
                risks.append(risk)
            Risk.objects.bulk_create(risks)
            risks = instance.risk_set.values("pk", "creator", "modifier")
    
            Action.objects.bulk_create(
                Action(creator_id=risk["creator"], modifier_id=risk["modifier"],
                       risk_id=risk["pk"]) for risk in risks)
    
            complexities = []
            for complexity in Complexity.objects.filter(prescription=None):
                complexity.pk = None
                complexity.prescription = instance
                complexities.append(complexity)
            Complexity.objects.bulk_create(complexities)
    
            for item in DefaultBriefingChecklist.objects.all():
                BriefingChecklist.objects.create(
                    prescription=instance, smeac=item.smeac, title=item.title)
    
            items = []
            for item in PriorityJustification.objects.filter(prescription=None):
                item.pk = None
                item.prescription = instance
                items.append(item)
            PriorityJustification.objects.bulk_create(items)
    
            # PBS-1286 - we only need one context statement.
            Context.objects.create(prescription=instance)
            OperationalOverview.objects.create(prescription=instance)
    
            logger.info("Finished creating risks...")

    @staticmethod
    @receiver(m2m_changed, sender=Prescription.purposes.through)
    def update_justification(sender, instance, action, reverse, model, pk_set,
                             **kwargs):
        """
        When a user selects relevant burn purposes, change our priority
        justification page to reflect only the relevant purposes. The changelist
        has its queryset filtered on whether or not the justification is relevant.
        """
        if action == 'post_add':
            if pk_set is not None:
                logger.debug("Updating priority justifications...")
                qs = instance.priorityjustification_set
                qs.filter(purpose__in=pk_set).update(relevant=True)
                qs.filter(~Q(purpose__in=pk_set)).update(relevant=False)
                logger.debug("Priority justifications updated...")
    
    @staticmethod
    @receiver(post_save, sender=Prescription)
    def create_state(sender, instance, created, **kwargs):
        """
        For each new prescription, create new state objects to track their
        completion.
        """
        from pbs.report.models import (SummaryCompletionState, BurnImplementationState,BurnClosureState,PostBurnChecklist)
        if created:
            for state in [SummaryCompletionState, BurnImplementationState,BurnClosureState]:
                state.objects.create(prescription=instance)
    
            for item in PostBurnChecklist.objects.filter(prescription=None):
                item.pk = None
                item.prescription = instance
                item.save()


class SuccessCriteriaListener(object):
    @staticmethod
    @receiver(post_save, sender=SuccessCriteria)
    def create_evaluation(sender, instance, created, **kwargs):
        """
        When a new success criteria is created, create an instance of an
        evaluation for that criteria.
        """
        from pbs.report.models import Evaluation
        if created:
            Evaluation.objects.create(criteria=instance)

