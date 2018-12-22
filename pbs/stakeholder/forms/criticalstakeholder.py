
from dpaw_utils import forms
from django.forms.formsets import DELETION_FIELD_NAME

from ..models import (CriticalStakeholder,)
import pbs.widgets

class CriticalStakeholderCleanMixin(object):
    pass


class CriticalStakeholderConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(CriticalStakeholder,"id",forms.fields.IntegerField,field_params={"required":False})
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden()
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
        all_fields = ('name','organization',"interest","id")
        editable_fields = ('id','name','organization',"interest")
        ordered_fields = ('name','organization','interest','id')


CriticalStakeholderListUpdateForm = forms.listupdateform_factory(CriticalStakeholderUpdateForm,min_num=4,max_num=4,extra=0)
        
