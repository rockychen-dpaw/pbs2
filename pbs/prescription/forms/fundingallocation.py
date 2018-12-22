
from dpaw_utils import forms
from django.forms.formsets import DELETION_FIELD_NAME

from pbs.prescription.models import (FundingAllocation,)
import pbs.widgets

class FundingAllocationCleanMixin(object):
    def clean_proportion(self):
        val = self.cleaned_data["proportion"]
        if val is None:
            return 0
        elif val < 0 or val > 100:
            raise forms.ValidationError("Must between 0 and 100")
        else:
            return val


class FundingAllocationConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(FundingAllocation,"id",forms.fields.IntegerField,field_params={"required":False})
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "allocation.edit":forms.widgets.Hidden(display_widget=pbs.widgets.FundingAllocationDisplay()),
            'proportion.edit':forms.widgets.NumberInput(attrs={"min":0,"max":100,"step":0.01}),
            "id.edit":forms.widgets.Hidden()
        }


class FundingAllocationBaseForm(FundingAllocationCleanMixin,FundingAllocationConfigMixin,forms.ModelForm):
    class Meta:
        pass

class FundingAllocationUpdateForm(FundingAllocationBaseForm):

    def __init__(self,parent_instance=None,*args,**kwargs):
        super(FundingAllocationUpdateForm,self).__init__(*args,**kwargs)
        if parent_instance:
            self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return self.cleaned_data.get(DELETION_FIELD_NAME, False) or self.instance.proportion == 0

    class Meta:
        model = FundingAllocation
        all_fields = ('allocation','proportion',"id")
        editable_fields = ('id','allocation','proportion')


FundingAllocationUpdateFormSet = forms.formset_factory(FundingAllocationUpdateForm,min_num=4,max_num=4,extra=0)
        
