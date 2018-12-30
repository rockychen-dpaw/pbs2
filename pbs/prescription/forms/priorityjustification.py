from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from ..models import (PriorityJustification,)

from dpaw_utils import forms

class PriorityJustificationCleanMixin(object):
    pass

class PriorityJustificationConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(PriorityJustification,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(PriorityJustification,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
            "criteria":"Criteria"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            "criteria.view":forms.widgets.Markdownify(),
            'rationale.edit':forms.widgets.Textarea(attrs={"class":"vTextField","rows":3}),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_successcriteria_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class PriorityJustificationMemberUpdateForm(PriorityJustificationCleanMixin,PriorityJustificationConfigMixin,forms.ListMemberForm):
    def __init__(self,parent_instance=None,*args,**kwargs):
        super(PriorityJustificationMemberUpdateForm,self).__init__(*args,**kwargs)
        if parent_instance:
            self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = PriorityJustification
        widths = {
            "criteria":"30%",
        }
        all_fields = ("rationale","priority","purpose","criteria","id")
        editable_fields = ('id',"rationale","priority")
        ordered_fields = ("id","purpose","criteria",'rationale',"priority")

PriorityJustificationListUpdateForm = forms.listupdateform_factory(PriorityJustificationMemberUpdateForm,min_num=0,max_num=100,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=False,can_add=False)

class PriorityJustificationBaseListForm(PriorityJustificationConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')

class PriorityJustificationListForm(PriorityJustificationBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(PriorityJustificationListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = PriorityJustification
        all_fields = ("criteria","id")
        widths = {
            "criteria":"30%",
        }
        editable_fields = []
        ordered_fields = ("criteria",)

