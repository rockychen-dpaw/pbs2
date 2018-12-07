
from django.utils import timezone

from dpaw_utils import forms

from pbs.prescription.models import (Prescription,Region,District)
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.utils import FinancialYear
from pbs.report.forms import (SummaryCompletionStateViewForm,BurnImplementationStateViewForm,BurnClosureStateViewForm)
from .fundingallocation import FundingAllocationUpdateFormSet
import pbs.widgets
import pbs.fields

class PrescriptionCleanMixin(object):
    def clean_non_calm_tenure_included(self):
        if self.cleaned_data["non_calm_tenure"]:
            value = self.cleaned_data.get("non_calm_tenure_included")
            if value:
                return value
            else:
                raise forms.ValidationError("Required.")
        else:
            return None

    def clean_non_calm_tenure_value(self):
        if self.cleaned_data["non_calm_tenure"]:
            value = self.cleaned_data.get("non_calm_tenure_value")
            if value:
                return value
            else:
                raise forms.ValidationError("Required.")
        else:
            return None

    def clean_non_calm_tenure_complete(self):
        if self.cleaned_data["non_calm_tenure"]:
            value = self.cleaned_data.get("non_calm_tenure_complete")
            if value is None:
                raise forms.ValidationError("Required.")
            else:
                return value
        else:
            return None

    def clean_non_calm_tenure_risks(self):
        if self.cleaned_data["non_calm_tenure"]:
            value = self.cleaned_data.get("non_calm_tenure_risks")
            if value:
                return value
            else:
                raise forms.ValidationError("Required.")
        else:
            return None

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
            return data

    def clean_last_year(self):
        data = self.cleaned_data.get("last_year")
        if self.cleaned_data.get("last_year_unknown"):
            return None
        elif not data:
            raise forms.ValidationError("This field is required.")
        else:
            return data

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
        return town if town else None

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
    def clean_all_allocations(self):
        total_proportion = 0
        for form in self["all_allocations"].formset:
            if not form.can_delete:
                total_proportion += form.cleaned_data['proportion']

        if total_proportion != 100:
            raise forms.ValidationError("Total proportion allocated must be 100%; currently {}%".format(total_proportion))

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
                on_layout="Unknown",
                off_layeout="{1}",
                edit_layout="last burnt season unknown? {0}<div id='id_{2}_body'>{1}</div>"
            ),
            "last_year_unknown":forms.fields.SwitchFieldFactory(Prescription,"last_year_unknown",("last_year",),
                reverse=True,
                on_layout="Unknown",
                off_layeout="{1}",
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
            "non_calm_tenure":forms.fields.SwitchFieldFactory(Prescription,"non_calm_tenure",("non_calm_tenure_included","non_calm_tenure_value","non_calm_tenure_complete","non_calm_tenure_risks"),
                on_layout=u"""
                {0}
                <br><br><span style="font-weight:bold"> Non-CALM Act tenure included * </span>
                <div class="freetext">{1}</div>
                <br><span style="font-weight:bold"> Public value in burn * </span>
                <div class="freetext">{2}</div>
                <br><span style="font-weight:bold"> Can the burn be completed safely without the inclusion of other tenure? </span> {3}
                <br><br><span style="font-weight:bold"> Risk based issues if other tenure not included * </span>
                <div class="freetext">{4}</div>
                """,
                edit_layout=u"""
                {0}
                <div id="id_{5}_body">
                    <div>
                        <span style="font-weight:bold">Non-CALM Act tenure included *</span>
                        {1}
                    </div>
                    <div>
                        <span style="font-weight:bold">Public value in burn * </span>
                        <br>{2}
                    </div>
                    <div>
                        <span style="font-weight:bold">Can the burn be completed safely without the inclusion of other tenure?</span> {3}
                    </div>
                    <div style="margin-top:3px">
                        <span style="font-weight:bold">Risk based issues if other tenure not included * </span>
                        <br>{4}
                    </div>
                </div>
                """
            ),
            "non_calm_tenure_complete.edit":forms.fields.ChoiceFieldFactory(Prescription.NON_CALM_TENURE_COMPLETE_CHOICES,field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "contentious.filter":forms.fields.BooleanChoiceFilter,
            "contingencies_migrated.filter":forms.fields.BooleanChoiceFilter,
            "loc_direction.edit":forms.fields.NullDirectionField,
            "loc_locality":forms.fields.ConditionalMultipleFieldFactory(Prescription,"loc_locality",("loc_distance","loc_direction","loc_town"),forms.fields.CharField,
                view_layouts=[
                    (lambda f:True if (f.get_fieldvalue("loc_distance") or f.get_fieldvalue("loc_direction") or f.get_fieldvalue("loc_town")) else False,
                        (u"""{0} - {1}km(s) {2} of {3}""",("loc_distance","loc_direction","loc_town"),True)),
                    (lambda f:True,(u"""Within the locality of {0}""",[],True))
                ],
                edit_layouts=[
                    (lambda f:True,(u"""
                    You must enter/select a value in all fields.<br>Alternatively, if entering only a locality (first input field), location will be stored as "Within the locality of ____"</span><br>
                    <table class='noborder'"><tr><td>{0} </td><td>-</td><td> {1}</td><td> km(s)</td><td> {2}</td> of <td>{3}</td></tr></table>
                    """,("loc_distance","loc_direction","loc_town"),True))
                ],
            ),
            "aircraft_burn.filter":forms.fields.BooleanChoiceFilter,
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
            "planning_status.view":pbs.fields.PrescriptionCorporateApprovalStatus,
            "planning_status.list":None,

            "endorsement_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.ENDORSEMENT_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "endorsement_status.view":pbs.fields.PrescriptionEndorsementStatus,
            "endorsement_status.list":None,

            "approval_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.APPROVAL_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "approval_status.view":pbs.fields.PrescriptionApprovalStatus,
            "approval_status.list":None,

            "ignition_status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.IGNITION_STATUS_CHOICES,
                choice_class=forms.fields.TypedMultipleChoiceField,
                field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),
            "ignition_commence_status":pbs.fields.PrescriptionIgnitionCommenceStatus,
            "ignition_complete_status":pbs.fields.PrescriptionIgnitionCompleteStatus,

            "status.filter":forms.fields.ChoiceFieldFactory(choices=Prescription.STATUS_CHOICES,
                    choice_class=forms.fields.TypedMultipleChoiceField,
                    field_params={"required":False,"coerce":forms.fields.coerce_int,"empty_value":None}),

            "financial_year":forms.fields.ChoiceFieldFactory(choices=FinancialYear().options(0,10)),
            "financial_year.filter":forms.fields.ChoiceFieldFactory(choices=FinancialYear().options(-5,5),
                    choice_class=forms.fields.TypedMultipleChoiceField,
                    field_params={"required":False,"empty_value":None}),

            "pre_state":forms.fields.FormFieldFactory(SummaryCompletionStateViewForm),
            "day_state":forms.fields.FormFieldFactory(BurnImplementationStateViewForm),
            "post_state":forms.fields.FormFieldFactory(BurnClosureStateViewForm),
            "all_allocations":forms.fields.FormSetFieldFactory(FundingAllocationUpdateFormSet,"""
            <table class="table table-bordered table-striped table-condensed">
                <thead>
                    <tr>
                        <th >Program allocation(s) *
                        {% if errors %}
                        <br>
                        {% for error in errors %}
                        <p class='text-error'><i class='icon-warning-sign'></i>{{ error }}</p>
                        {% endfor %}
                        {% endif %}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <!-- This is the new formsets for PBS-1551 -->
		    {% for form in formset %}
                    <tr>
                        <th> Allocation code </th>
                        <td>{{form.id}}{{form.allocation}}</td>
                        <th> Proportion of funding [%] </th>
                        <td>{{form.proportion}}</td>
                    </tr>
		    {% endfor %}
                    
                </tbody>
            </table>

            """)
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            'description.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'forest_blocks.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'rationale.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'bushfire_act_zone.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'prohibited_period.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'short_code.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'treatment_percentage.edit':forms.widgets.NumberInput(attrs={"min":0,"max":100}),
            "burn_id.list":forms.widgets.HyperlinkFactory("burn_id","prescription:prescription_home"),
            "name.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "non_calm_tenure.edit":forms.widgets.NullBooleanSelect(),
            "last_year.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "last_season.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "loc_distance.edit":forms.widgets.NumberInput(attrs={"min":0,"style":"width:60px"}),
            "loc_direction.edit":forms.widgets.Select(),
            "financial_year.edit":forms.widgets.Select(attrs={"style":"width:120px"}),
            "purposes.edit":forms.widgets.TemplateWidgetFactory(forms.widgets.CheckboxSelectMultiple,"""
                <span >Burn purpose text must be updated for Biodiversity Management, Bushfire Risk Management and Vegetation Management purposes.
                    <br>All other purposes will use the default text as per Appendix 4 in the Prescribed Fire Manual.</span>
                <hr class="id_purposes_hr">
                {0}
            """),
            "contentious_rationale.edit":forms.widgets.Textarea(attrs={"class":"vTextField"}),
            "contentious.view":forms.widgets.ImgBooleanDisplay(),
            "aircraft_burn.list":forms.widgets.ImgBooleanDisplay(),
            "aircraft_burn.view":pbs.widgets.IgnitionTypeDisplay(),
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
            "maximum_risk.view":pbs.widgets.RiskLevelDisplay(),
            "maximum_draft_risk.view":pbs.widgets.RiskLevelDisplay(),
            "maximum_complexity.view":pbs.widgets.ComplexityRatingDisplay(),
            "priority.view":pbs.widgets.PrescriptionPriorityDisplay,
            "planning_status_modified":forms.widgets.DatetimeDisplay("%d-%m-%Y"),
            "endorsement_status_modified":forms.widgets.DatetimeDisplay("%d-%m-%Y"),
            "approval_status_modified":forms.widgets.DatetimeDisplay("%d-%m-%Y"),
            "current_approval_valid_period":forms.widgets.DatetimeDisplay("%d-%m-%Y"),
            "ignition_completed_date":forms.widgets.DatetimeDisplay("%d-%m-%Y"),
            'status.view':pbs.widgets.PrescriptionStatusIconDisplay(),
            'status.list':pbs.widgets.PrescriptionStatusDisplay(),
            "tenures.edit":forms.widgets.FilteredSelectMultiple("Burn Tenures",False),
            "fuel_types.edit":forms.widgets.FilteredSelectMultiple("Fuel Types",False),
            "shires.edit":forms.widgets.FilteredSelectMultiple("Shires",False),
            "forecast_areas.edit":forms.widgets.FilteredSelectMultiple("Forecast Areas",False),
            "non_calm_tenure_complete.edit":forms.widgets.RadioSelect(),
            "non_calm_tenure_included.edit":forms.widgets.Textarea(attrs={"style":"width:90%;"}),
            "non_calm_tenure_value.edit":forms.widgets.Textarea(attrs={"style":"width:90%;"}),
            "non_calm_tenure_risks.edit":forms.widgets.Textarea(attrs={"style":"width:90%;"})
        }

class PrescriptionFilterForm(PrescriptionConfigMixin,forms.FilterForm):
    all_buttons = [
        BUTTON_ACTIONS["update_selection"],
    ]

    class Meta:
        model = Prescription
        purpose = 'filter'
        fields = ('region','district','financial_year','contentious','aircraft_burn','priority',
                  'planning_status','endorsement_status','approval_status','ignition_status','status'
                  )
        other_fields = ('contingencies_migrated',)


class PrescriptionBaseForm(PrescriptionCleanMixin,PrescriptionConfigMixin,forms.ModelForm):
    class Meta:
        pass

class PrescriptionViewForm(PrescriptionBaseForm):
    all_buttons = [
    ]
    def __init__(self, *args, **kwargs):
        super(PrescriptionViewForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Prescription
        purpose = "view"
        fields = ('burn_id','planned_season', 'financial_year', 'name', 'description', 'region',
                  'district','last_year_unknown', 'last_year',
                  'last_season_unknown','last_season', 'forest_blocks', 
                  'contentious','contentious_rationale', 'purposes',
                  'aircraft_burn', 'priority', 'area', 'treatment_percentage',
                  'perimeter', 'remote_sensing_priority','rationale','planning_status','endorsement_status','approval_status',
                  'ignition_status','ignition_completed_date','status')
        other_fields = ('loc_locality','loc_distance','loc_direction','loc_town',"maximum_risk","maximum_complexity","pre_state","day_state","post_state"
                ,'planning_status_modified','endorsement_status_modified','approval_status_modified','current_approval_valid_period','current_approval_approver'
                ,'ignition_commenced_date','ignition_commence_status','ignition_complete_status')

class PrescriptionUpdateForm(PrescriptionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
    ]

    def get_update_success_message(self) :
        return "{} summary updated successfully".format(self.instance.burn_id)

    class Meta:
        model = Prescription
        fields = ('burn_id','name','description','financial_year','last_season_unknown','last_season','last_year_unknown','last_year',
            'region','district','forest_blocks','priority','rationale','contentious','contentious_rationale','aircraft_burn',
            'remote_sensing_priority','purposes','area','perimeter','tenures','fuel_types','shires','forecast_areas','bushfire_act_zone',
            "non_calm_tenure","non_calm_tenure_included","non_calm_tenure_value","non_calm_tenure_complete","non_calm_tenure_risks",
            'treatment_percentage','prohibited_period','prescribing_officer','short_code','endorsement_status',
            'approval_status',
            'planning_status','ignition_status','status'
        )
        editable_fields = ('forest_blocks','aircraft_burn','remote_sensing_priority','purposes','area','perimeter','tenures',
            "non_calm_tenure","non_calm_tenure_included","non_calm_tenure_value","non_calm_tenure_complete","non_calm_tenure_risks",
            'fuel_types','shires','forecast_areas','bushfire_act_zone','treatment_percentage','prohibited_period','prescribing_officer',
            'short_code','all_allocations'
        )
        other_fields = ('loc_locality','loc_distance','loc_direction','loc_town','created','modified','maximum_risk','maximum_complexity','all_allocations',
                "planning_status_modified","endorsement_status_modified","approval_status_modified","current_approval_approver","current_approval_valid_period")
        extra_update_fields = ('modifier_id','modified')

class DraftPrescriptionUpdateForm(PrescriptionUpdateForm):
    class Meta:
        model = Prescription
        editable_fields = ('name','description','financial_year','last_season','last_season_unknown','last_year','last_year_unknown',
            'loc_locality','loc_distance','loc_direction','loc_town',
            'forest_blocks','priority','rationale','contentious','contentious_rationale','aircraft_burn','remote_sensing_priority','purposes','area','perimeter',
            "non_calm_tenure","non_calm_tenure_included","non_calm_tenure_value","non_calm_tenure_complete","non_calm_tenure_risks",
            'tenures','fuel_types','shires','forecast_areas','bushfire_act_zone','treatment_percentage','prohibited_period','prescribing_officer',
            'short_code','all_allocations'
        )
        extra_update_fields = ('location','modifier_id','modified')

class PrescriptionCreateForm(PrescriptionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
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
        OPTION_ACTIONS["delete_selected_epfp"],
        OPTION_ACTIONS["export_to_csv"],
        OPTION_ACTIONS["burn_summary_to_csv"],
        OPTION_ACTIONS["delete_approval_endorsement"],
        OPTION_ACTIONS["carry_over_burns"],
        OPTION_ACTIONS["bulk_corporate_approve"],
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

