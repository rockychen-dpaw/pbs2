from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (Action,)
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)

from dpaw_utils import forms

class ActionCleanMixin(object):
    pass

class ActionConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Action,"id",forms.fields.IntegerField,field_params={"required":False}),
            "multiple":forms.fields.AliasFieldFactory(Action,"id",field_class=forms.fields.IntegerField),
            "delete":forms.fields.AliasFieldFactory(Action,"id",field_class=forms.fields.IntegerField),
            "category":forms.fields.IntegerField,
        }
        labels = {
            "delete":"",
            "multiple":"Multiple?"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            'details.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            "risk_name":forms.widgets.HyperlinkFactory("risk_name","risk:prescription_action_update",ids=[("id","pk"),("risk__prescription__id","ppk")]),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_successcriteria_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class ActionFilterForm(ActionConfigMixin,forms.FilterForm):
    all_buttons = [
        BUTTON_ACTIONS["update_selection"],
    ]

    class Meta:
        model = Action
        purpose = (('filter','edit'),"view")
        all_fields = ("relevant","category")


class ActionBaseForm(ActionCleanMixin,ActionConfigMixin,forms.ModelForm):
    class Meta:
        pass

class ActionCreateForm(forms.RequestUrlMixin,ActionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = Action
        all_fields = ("risk__category","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement")
        editable_fields = ("relevant","details","pre_burn","day_of_burn","post_burn","context_statement")
        ordered_fields = ("risk__category","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement")

class ActionUpdateForm(forms.RequestUrlMixin,ActionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = Action
        all_fields = ("risk__category","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement")
        editable_fields = ("relevant","details","pre_burn","day_of_burn","post_burn","context_statement")
        ordered_fields = ("risk__category","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement")

class ActionMemberUpdateForm(forms.RequestUrlMixin,ActionCleanMixin,ActionConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        pass

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = Action
        widths = {
            "delete":"16px"
        }
        all_fields = ("risk__category","id","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement","delete")
        editable_fields = ("id","relevant","details","pre_burn","day_of_burn","post_burn","context_statement")
        ordered_fields = ("id","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement","delete")

ActionListUpdateForm = forms.listupdateform_factory(ActionMemberUpdateForm,min_num=0,max_num=400,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=False)

class ActionBaseListForm(ActionConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ActionListForm(ActionBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(ActionListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Action
        all_fields = ("id","details")
        widths = {
        }
        editable_fields = []
        ordered_fields = ("id","details")

