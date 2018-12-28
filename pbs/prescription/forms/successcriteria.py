from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from ..models import (SuccessCriteria,)

from dpaw_utils import forms

class SuccessCriteriaCleanMixin(object):
    pass

class SuccessCriteriaConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(SuccessCriteria,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(SuccessCriteria,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":""
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            'criteria.edit':forms.widgets.Textarea(attrs={"class":"vTextField","rows":3}),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_successcriteria_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class SuccessCriteriaMemberUpdateForm(SuccessCriteriaCleanMixin,SuccessCriteriaConfigMixin,forms.ListMemberForm):
    def __init__(self,parent_instance=None,*args,**kwargs):
        super(SuccessCriteriaMemberUpdateForm,self).__init__(*args,**kwargs)
        if parent_instance:
            self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = SuccessCriteria
        all_fields = ("criteria","id","delete")
        editable_fields = ('id',"criteria")
        ordered_fields = ("id",'criteria',"delete")

SuccessCriteriaListUpdateForm = forms.listupdateform_factory(SuccessCriteriaMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True)

class SuccessCriteriaBaseListForm(SuccessCriteriaConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')

class SuccessCriteriaListForm(SuccessCriteriaBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(SuccessCriteriaListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = SuccessCriteria
        all_fields = ("criteria","id")
        
        editable_fields = []
        ordered_fields = ("criteria",)

