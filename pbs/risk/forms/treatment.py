from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (Treatment,)

from dpaw_utils import forms

class TreatmentCleanMixin(object):
    pass

class TreatmentConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Treatment,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(Treatment,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
            "description":"Treatment"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            "delete.view":forms.widgets.HyperlinkFactory("id","risk:prescription_register_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class TreatmentBaseForm(TreatmentCleanMixin,TreatmentConfigMixin,forms.ModelForm):
    class Meta:
        model = Treatment
        all_fields = ()

class TreatmentMemberUpdateForm(TreatmentCleanMixin,TreatmentConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        pass

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get('description')

    class Meta:
        model = Treatment
        widths = {
            "description":"30%",
        }
        all_fields = ("description","delete","id")
        editable_fields = ("description","id")
        ordered_fields = ("id","description","delete")

TreatmentListUpdateForm = forms.listupdateform_factory(TreatmentMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=True)

class TreatmentBaseListForm(TreatmentConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')

class TreatmentListForm(TreatmentBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(TreatmentListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Treatment
        widths = {
            "complete":"100px",
        }
        all_fields = ("register__description","description","complete")
        editable_fields = []
        ordered_fields = ("register__description","description","complete")

