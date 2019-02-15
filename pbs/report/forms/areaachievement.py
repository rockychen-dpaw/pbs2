from django_select2.forms import Select2MultipleWidget

from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.report.models import (AreaAchievement,)

from dpaw_utils import forms

class AreaAchievementCleanMixin(object):
    pass

class AreaAchievementConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "delete":forms.fields.AliasFieldFactory(AreaAchievement,"id",field_class=forms.fields.IntegerField),
            "id":forms.fields.OverrideFieldFactory(AreaAchievement,"id",forms.fields.IntegerField,field_params={"required":False}),

            "total":forms.fields.HtmlStringField("Total"),
            "total_area_treated.list":forms.fields.SummaryField("area_treated"),
            "total_area_estimate.list":forms.fields.SummaryField("area_estimate"),
            "total_edging_length.list":forms.fields.SummaryField("edging_length"),
            "total_edging_depth_estimate.list":forms.fields.SummaryField("edging_depth_estimate"),
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            'ignition.edit':forms.widgets.DateInput(maxdate=False,attrs={"style":"width:80px"}),
            'date_escaped.edit':forms.widgets.DateInput(maxdate=False,attrs={"style":"width:80px"}),
            'dpaw_fire_no.edit':forms.widgets.TextInput(attrs={"style":"width:100px"}),
            'dfes_fire_no.edit':forms.widgets.TextInput(attrs={"style":"width:100px"}),
            'area_treated.edit':forms.widgets.NumberInput(attrs={"style":"width:70px","step":"0.1"}),
            'area_estimate.edit':forms.widgets.NumberInput(attrs={"style":"width:70px","step":"0.1"}),
            'edging_length.edit':forms.widgets.NumberInput(attrs={"style":"width:50px","step":"0.1"}),
            'edging_depth_estimate.edit':forms.widgets.NumberInput(attrs={"style":"width:50px","step":"0.1"}),
            "ignition_types.edit":Select2MultipleWidget(),
            "ignition_types.view":forms.widgets.ListDisplayFactory(forms.widgets.TextDisplay),
            "delete.view":forms.widgets.HyperlinkFactory("id","report:prescription_areaachievement_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class AreaAchievementBaseForm(AreaAchievementCleanMixin,AreaAchievementConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class AreaAchievementUpdateForm(AreaAchievementBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
    ]
    class Meta:
        model = AreaAchievement
        all_fields = ("ignition","ignition_types","area_treated","area_estimate","edging_length","edging_depth_estimate","dpaw_fire_no","dfes_fire_no","date_escaped")


class AreaAchievementMemberUpdateForm(AreaAchievementCleanMixin,AreaAchievementConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") \
           and not self.cleaned_data.get("ignition")  \
           and not self.cleaned_data.get("ignition_types") \
           and not self.cleaned_data.get("area_treated") \
           and not self.cleaned_data.get("area_estimate") \
           and not self.cleaned_data.get("edging_length") \
           and not self.cleaned_data.get("edging_depth_estimate") \
           and not self.cleaned_data.get("dpaw_fire_no") \
           and not self.cleaned_data.get("dfes_fire_no") \
           and not self.cleaned_data.get("date_escaped") 

    class Meta:
        model = AreaAchievement
        widths = {
            "delete":"16px",
        }
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("id","ignition","ignition_types","area_treated","area_estimate","edging_length","edging_depth_estimate","dpaw_fire_no","dfes_fire_no","date_escaped","delete")
        editable_fields = ("id","ignition","ignition_types","area_treated","area_estimate","edging_length","edging_depth_estimate","dpaw_fire_no","dfes_fire_no","date_escaped")
        listfooter_fields = [((None,0),"total",None,"total_area_treated","total_area_estimate","total_edging_length","total_edging_depth_estimate",None,None,None,None)]

AreaAchievementListUpdateForm = forms.listupdateform_factory(AreaAchievementMemberUpdateForm,min_num=0,max_num=400,extra=1,primary_field="id",all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=True)

class AreaAchievementBaseListForm(AreaAchievementConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class AreaAchievementListForm(AreaAchievementBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["save"],
    ]
    def __init__(self, *args, **kwargs):
        super(AreaAchievementListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = AreaAchievement
        all_fields = ("ignition","ignition_types","area_treated","area_estimate","edging_length","edging_depth_estimate","dpaw_fire_no","dfes_fire_no","date_escaped")
        editable_fields = []
        listfooter_fields = [((None,0),"total",None,"total_area_treated","total_area_estimate","total_edging_length","total_edging_depth_estimate",None,None,None,None)]

