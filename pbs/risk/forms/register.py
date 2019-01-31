from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (Register,)

from dpaw_utils import forms

class RegisterCleanMixin(object):
    pass

class RegisterConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Register,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(Register,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            'description.edit':forms.widgets.Textarea(attrs={"class":"vTextField","rows":3}),
            "delete.view":forms.widgets.HyperlinkFactory("id","risk:prescription_register_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class RegisterBaseForm(RegisterCleanMixin,RegisterConfigMixin,forms.ModelForm):
    class Meta:
        model = Register
        all_fields = ()

class RegisterMemberUpdateForm(RegisterCleanMixin,RegisterConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get('description')

    class Meta:
        model = Register
        widths = {
            "description":"30%",
        }
        all_fields = ("description","draft_consequence","draft_likelihood","draft_risk_level","alarp","delete","id")
        editable_fields = ("description","draft_consequence","draft_likelihood","alarp","id")
        ordered_fields = ("id","description","draft_consequence","draft_likelihood","draft_risk_level","alarp","delete")

RegisterListUpdateForm = forms.listupdateform_factory(RegisterMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=True)

class RegisterBaseListForm(RegisterConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class RegisterListForm(RegisterBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(RegisterListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Register
        widths = {
            "criteria":"30%",
        }
        all_fields = ("description","draft_consequence","draft_likelihood","draft_risk_level","alarp","id")
        editable_fields = []
        ordered_fields = ("id","description","draft_consequence","draft_likelihood","draft_risk_level","alarp")

