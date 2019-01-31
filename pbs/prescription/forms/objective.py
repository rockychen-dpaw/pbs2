
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.prescription.models import (Objective,)

from dpaw_utils import forms

class ObjectiveCleanMixin(object):
    pass

class ObjectiveConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Objective,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(Objective,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":""
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            'objectives.edit':forms.widgets.Textarea(attrs={"class":"vTextField","rows":3}),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_objective_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class ObjectiveMemberUpdateForm(ObjectiveCleanMixin,ObjectiveConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("objectives")

    class Meta:
        model = Objective
        all_fields = ("objectives","id","delete")
        editable_fields = ('id',"objectives")
        ordered_fields = ("id",'objectives',"delete")

ObjectiveListUpdateForm = forms.listupdateform_factory(ObjectiveMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True)

class ObjectiveBaseListForm(ObjectiveConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ObjectiveListForm(ObjectiveBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(ObjectiveListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Objective
        all_fields = ("objectives",)
        
        editable_fields = []
        ordered_fields = ("objectives",)

