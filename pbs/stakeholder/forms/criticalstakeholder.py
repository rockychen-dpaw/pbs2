
from dpaw_utils import forms
from django.forms.formsets import DELETION_FIELD_NAME

from ..models import (CriticalStakeholder,)
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
            'organization.edit':forms.widgets.TextInput(attrs={"class":"vTextField"}),
            'interest.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","stakeholder:prescription_criticalstakeholders_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<a class='inline-deletelink' title='Delete' href='{url}'><img src='/static/img/delete.png' style='width:32px;height:32px'> </a>")
        }
        labels = {
            "delete":""
        }


class CriticalStakeholderBaseForm(CriticalStakeholderCleanMixin,CriticalStakeholderConfigMixin,forms.ListMemberForm):
    class Meta:
        pass

class CriticalStakeholderUpdateForm(CriticalStakeholderBaseForm):

    def __init__(self,parent_instance=None,*args,**kwargs):
        super(CriticalStakeholderUpdateForm,self).__init__(*args,**kwargs)
        if parent_instance:
            self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return False

    class Meta:
        model = CriticalStakeholder
        all_fields = ('name','organization',"interest","id","delete")
        editable_fields = ('id','name','organization',"interest")
        ordered_fields = ("id",'name','organization','interest',"delete")


CriticalStakeholderListUpdateForm = forms.listupdateform_factory(CriticalStakeholderUpdateForm,min_num=1,max_num=100,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')])
        
class CriticalStakeholderBaseListForm(CriticalStakeholderConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')


class CriticalStakeholderListForm(CriticalStakeholderBaseListForm):
    class Meta:
        model = CriticalStakeholder
        all_fields = ('name','organization',"interest","id")
        ordered_fields = ("id",'name','organization','interest')
