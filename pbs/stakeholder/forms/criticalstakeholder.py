from dpaw_utils import forms
from django.forms.formsets import DELETION_FIELD_NAME

from pbs.stakeholder.models import (CriticalStakeholder,)
import pbs.widgets
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)

class CriticalStakeholderCleanMixin(object):
    pass


class CriticalStakeholderConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(CriticalStakeholder,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(CriticalStakeholder,"id",field_class=forms.fields.IntegerField)
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            'name.edit':forms.widgets.TextInput(attrs={"class":"vTextField"}),
            'organisation.edit':forms.widgets.TextInput(attrs={"class":"vTextField"}),
            'interest.edit':forms.widgets.Textarea(attrs={"class":"vTextField","rows":3}),
            "delete.view":forms.widgets.HyperlinkFactory("id","stakeholder:prescription_criticalstakeholder_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }
        labels = {
            "delete":""
        }


class CriticalStakeholderMemberUpdateForm(CriticalStakeholderCleanMixin,CriticalStakeholderConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("name") and not self.cleaned_data.get("interest")

    class Meta:
        model = CriticalStakeholder
        all_fields = ('name','organisation',"interest","id","delete")
        editable_fields = ('id','name','organisation',"interest")
        ordered_fields = ("id",'name','organisation','interest',"delete")


CriticalStakeholderListUpdateForm = forms.listupdateform_factory(CriticalStakeholderMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True)
        
class CriticalStakeholderBaseListForm(CriticalStakeholderConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))


class CriticalStakeholderListForm(CriticalStakeholderBaseListForm):
    class Meta:
        model = CriticalStakeholder
        all_fields = ('name','organization',"interest","id")
        ordered_fields = ("id",'name','organization','interest')
