from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (Risk,)

from dpaw_utils import forms

class RiskCleanMixin(object):
    pass

class RiskConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Risk,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(Risk,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            "category.list":forms.widgets.TemplateDisplay(forms.widgets.DisplayWidget(),"<span style='font-weight:bold'>{}</span>"),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_successcriteria_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class RiskBaseForm(RiskCleanMixin,RiskConfigMixin,forms.ModelForm):
    class Meta:
        model = Risk
        all_fields = ()

class CustomRiskCreateForm(forms.RequestUrlMixin,RiskBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    def __init__(self,*args,**kwargs):
        kwargs["instance"] = Risk(custom=True,risk=Risk.RISK_UNASSESSED)
        super(CustomRiskCreateForm,self).__init__(*args,**kwargs)

    class Meta:
        model = Risk
        all_fields = ("category","name")
        editable_fields = ("category","name")
        ordered_fields = ("category","name")


class RiskMemberUpdateForm(RiskCleanMixin,RiskConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = Risk
        widths = {
            "criteria":"30%",
        }
        all_fields = ("name","category","risk","custom","id")
        editable_fields = ("name","category","risk","custom","id")
        ordered_fields = ("id","name","category","risk","custom")

RiskListUpdateForm = forms.listupdateform_factory(RiskMemberUpdateForm,min_num=0,max_num=100,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=False,can_add=False)

class RiskBaseListForm(RiskConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class RiskListForm(RiskBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(RiskListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Risk
        all_fields = ("name","category","risk","custom","id")
        widths = {
        }
        editable_fields = []
        ordered_fields = ("id","name","category","risk","custom")

