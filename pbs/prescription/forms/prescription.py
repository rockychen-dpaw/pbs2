
from django.utils import timezone

from dpaw_utils import forms

from pbs.prescription.models import (Prescription,Region,District)
from pbs.forms import (FORM_ACTIONS,LIST_ACTIONS)
from pbs.utils import FinancialYear
import pbs.widgets

class PrescriptionCleanMixin(object):
    def clean_district(self):
        """
        Force the user to select a district.
        """
        data = self.cleaned_data['district']
        if data is None:
            raise forms.ValidationError("This field is required.")
        # FIXME: hack to raise a form validation error on creation.
        if data.archive_date:
            raise forms.ValidationError("You cannot select an archived District")
        return data

    def clean_last_season(self):
        data = self.cleaned_data.get("last_season")
        if self.cleaned_data.get("last_season_unknown"):
            return None
        elif not data:
            raise forms.ValidationError("This field is required.")
        else:
            return None

    def clean_last_year(self):
        data = self.cleaned_data.get("last_year")
        if self.cleaned_data.get("last_year_unknown"):
            return None
        elif not data:
            raise forms.ValidationError("This field is required.")
        else:
            return None

    def clean_loc_locality(self):
        data = self.cleaned_data.get("loc_locality")
        if data:
            return data
        else:
            raise forms.ValidationError("This field is required.")

    def clean_loc_town(self):
        distance = self.cleaned_data.get("loc_distance")
        direction = self.cleaned_data.get("loc_direction")
        town = self.cleaned_data.get("loc_town")
        if distance or direction or town:
            if not distance:
                self.add_error("loc_distance",forms.ValidationError("This field is required"))
            if not direction:
                self.add_error("loc_direction",forms.ValidationError("This field is required"))
            if not town:
                raise forms.ValidationError("This field is required.")

    def clean_contentious(self):
        data = self.cleaned_data.get("contentious")
        if data is None:
            raise forms.ValidationError("You must select Yes or No for Contentious.")
        else:
            return data

    def clean_contentious_rationale(self):
        data = self.cleaned_data.get("contentious_rationale")
        if not self.cleaned_data.get("contentious"):
            return None
        elif not data:
            raise forms.ValidationError("A contentious burn requires a contentious rationale.")
        else:
            return data

    def clean_financial_year(self):
        data = self.cleaned_data.get("financial_year")
        if not data:
            raise forms.ValidationError("This field is required.")

        financial_year = FinancialYear()
        year = financial_year.parse(data)

        if financial_year.is_before(year):
            raise forms.ValidationError("Financial year burnt must be in the current financial year or in the future.")

        return financial_year.format(year)

    """
    def clean_last_year(self):
        data = self.cleaned_data.get("last_year")
        if data and data > timezone.now().year:
            raise ValidationError("Last year burnt must not be in the future.")
        if data and data < 1900:
            raise ValidationError("Last year burnt must be after 1900.")

        return data

    def clean_planned_year(self):
        data = self.cleaned_data.get("planned_year")
        if data and data < timezone.now().year:
            raise ValidationError("Planned year burnt must be in the current year or in the future.")

        return data
    """

class PrescriptionConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "last_season_unknown":forms.fields.SwitchFieldFactory(Prescription,"last_season_unknown",("last_season",),
                reverse=True,
                edit_layout="last burnt season unknown? {0}<div id='id_{2}_body'>{1}</div>"
            ),
            "last_year_unknown":forms.fields.SwitchFieldFactory(Prescription,"last_year_unknown",("last_year",),
                reverse=True,
                edit_layout="last burnt year unknown? {0}<div id='id_{2}_body'>{1}</div>"
            ),
            "contentious":forms.fields.SwitchFieldFactory(Prescription,"contentious",("contentious_rationale",),
                edit_layout="""
                {0}
                <div id="id_{2}_body">
                    <div style="font-weight:bold">Contentious Rationale</div>
                    {1}
                </div>

                """
            ),
            "loc_direction.edit":forms.fields.NullDirectionField,
            "loc_locality":forms.fields.MultipleFieldFactory(Prescription,"loc_locality",("loc_distance","loc_direction","loc_town"),forms.fields.CharField,
                layout="""
                You must enter/select a value in all fields.<br>Alternatively, if entering only a locality (first input field), location will be stored as "Within the locality of ____"</span><br>
                <table class='noborder'"><tr><td>{0} </td><td>-</td><td> {1}</td><td> km(s)</td><td> {2}</td> of <td>{3}</td></tr></table>
                """),
            "financial_year":forms.fields.ChoiceFieldFactory(choices=FinancialYear().options(0,10)),

            "aircraft_burn.filter":forms.fields.BooleanChoiceFilter,
            "contingencies_migrated.filter":forms.fields.BooleanChoiceFilter,
            "contentious.filter":forms.fields.BooleanChoiceFilter,
            "region.filter":forms.fields.ChoiceFieldFactory(choices=Region.objects.all().order_by("name"),type_name="region"
                ,choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "district.filter":forms.fields.ChoiceFieldFactory(choices=District.objects.all().order_by("region__name","name"),
                choice_class=forms.fields.TypedMultipleChoiceField,type_name="district",
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "priority.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.PRIORITY_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "planning_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.PLANNING_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "endorsement_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.ENDORSEMENT_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "approval_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.APPROVAL_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "ignition_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.IGNITION_STATUS_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.STATUS_CHOICES,
                    choice_class=forms.fields.TypedMultipleChoiceField,
                    field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "financial_year.filter":forms.fields.ChoiceFieldFactory(choices=FinancialYear().options(-5,5),
                    choice_class=forms.fields.TypedMultipleChoiceField,
                    field_params={"required":False,"empty_value":None}),
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "burn_id.list":forms.widgets.HyperlinkFactory("burn_id","prescription:prescription_update"),
            "name.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "last_year.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "last_season.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "loc_distance.edit":forms.widgets.NumberInput(attrs={"min":0,"style":"width:60px"}),
            "loc_direction.edit":forms.widgets.Select(),
            "financial_year.edit":forms.widgets.Select(attrs={"style":"width:120px"}),
            "purposes.edit":forms.widgets.CheckboxSelectMultiple(),
            "contentious_rationale.edit":forms.widgets.Textarea(attrs={"style":"width:90%"}),
            "contentious.view":forms.widgets.ImgBooleanDisplay(),
            "aircraft_burn.view":forms.widgets.ImgBooleanDisplay(),
            "remote_sensing_priority.view":pbs.widgets.RemoteSensingPriorityDisplay(),
            "planning_status.view":pbs.widgets.PlanningStatusDisplay(),
            "modified.view":forms.widgets.DatetimeDisplay(),
            "contingencies_migrated.view":forms.widgets.ImgBooleanDisplay(),
            "status.view":pbs.widgets.PrescriptionStatusDisplay(),
            "ignition_status.view":pbs.widgets.IgnitionStatusDisplay(),
            "approval_status.view":pbs.widgets.ApprovalStatusDisplay(),
            "endorsement_status.view":pbs.widgets.EndorsementStatusDisplay(),
            "region.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Region"}),
            "district.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"District"}),
            "financial_year.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Financial Year"}),
            "contentious.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Contentious"}),
            "aircraft_burn.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Aircraft Burn?"}),
            "priority.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Overall Priority"}),
            "planning_status.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Planning Status"}),
            "endorsement_status.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Endorsement Status"}),
            "approval_status.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Approval Status"}),
            "ignition_status.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Ignition Status"}),
            "status.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Status"}),
            "contingencies_migrated.filter":forms.widgets.DropdownMenuSelectMultiple(attrs={"title":"Contingencies Migrated"}),

        }

class PrescriptionBaseForm(PrescriptionCleanMixin,PrescriptionConfigMixin,forms.ModelForm):
    class Meta:
        pass

class PrescriptionFilterForm(PrescriptionConfigMixin,forms.FilterForm):
    all_actions = [
        FORM_ACTIONS["update_selection"],
    ]

    class Meta:
        model = Prescription
        purpose = 'filter'
        fields = ('region','district','financial_year','contentious','aircraft_burn','priority',
                  'planning_status','endorsement_status','approval_status','ignition_status','status'
                  )
        other_fields = ('contingencies_migrated',)


class PrescriptionCreateForm(PrescriptionBaseForm):
    all_actions = [
        FORM_ACTIONS["save"],
        FORM_ACTIONS["back"]
    ]
    def __init__(self, *args, **kwargs):
        super(PrescriptionCreateForm, self).__init__(*args, **kwargs)
        self.fields['purposes'].error_messages.update({
            'required': 'There must be at least one burn purpose.'
        })

    class Meta:
        model = Prescription
        fields = ('planned_season', 'financial_year', 'name', 'description', 'region',
                  'district','last_year_unknown', 'last_year',
                  'last_season_unknown','last_season', 'forest_blocks', 
                  'contentious','contentious_rationale', 'purposes',
                  'aircraft_burn', 'priority', 'area', 'treatment_percentage',
                  'perimeter', 'remote_sensing_priority','rationale')
        other_fields = ('loc_locality','loc_distance','loc_direction','loc_town')

class PrescriptionBaseListForm(PrescriptionConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')

class PrescriptionListForm(PrescriptionBaseListForm):
    all_actions = [
        LIST_ACTIONS["delete_selected_epfp"],
        LIST_ACTIONS["export_to_csv"],
        LIST_ACTIONS["burn_summary_to_csv"],
        LIST_ACTIONS["delete_approval_endorsement"],
        LIST_ACTIONS["carry_over_burns"],
        LIST_ACTIONS["bulk_corporate_approve"],
    ]
    def __init__(self, *args, **kwargs):
        super(PrescriptionListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Prescription
        fields = ('burn_id','name','region','district','financial_year','contentious','aircraft_burn','priority','remote_sensing_priority',
                'planning_status','endorsement_status','approval_status','ignition_status','status','prescribing_officer')
        other_fields = ('modified','contingencies_migrated',"approval_expiry")
        
        field_classes_config = {
            "contentious":None
        }
        editable_fields = []
        ordered_fields = ('burn_id','name','region','district','financial_year','contentious','aircraft_burn','priority',
                'remote_sensing_priority','planning_status','endorsement_status','approval_status','approval_expiry','ignition_status',
                'status','prescribing_officer','modified','contingencies_migrated')
        toggleable_fields = ('financial_year','contentious','aircraft_burn','priority','remote_sensing_priority','planning_status',
                'endorsement_status','approval_status','approval_expiry','ignition_status','status','prescribing_officer','modified','contingencies_migrated')
        default_toggled_fields = ('financial_year','contentious','aircraft_burn','priority','remote_sensing_priority','planning_status')
        sortable_fields = ("burn_id","name","region","district","financial_year")

