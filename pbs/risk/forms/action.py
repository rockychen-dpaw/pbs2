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
            "multiple":forms.fields.AliasFieldFactory(Action,"index",field_class=forms.fields.IntegerField),
            "delete":forms.fields.AliasFieldFactory(Action,"id",field_class=forms.fields.IntegerField),
            "category":forms.fields.IntegerField,
        }
        labels = {
            "delete":"",
            "preburn_action_delete":"",
            "multiple":"Multiple?",
            "risk_name":"Action"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            'details.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'pre_burn_explanation.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'pre_burn_completer.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            'pre_burn_completed.edit':forms.widgets.DatetimeInput(attrs={"style":"width:115px"}),
            "multiple.view":forms.widgets.HyperlinkFactory("index","risk:prescription_multipleaction_add",ids=[("id","actionpk"),("risk__prescription__id","ppk")],template=lambda value:"""<button class='btn btn-mini btn-success' onclick="window.location='{url}'" type='button'>Add</button>""" if value == 1 else "" ),
            "risk_name.view":forms.widgets.HyperlinkFactory("risk_name","risk:prescription_action_update",ids=[("id","pk"),("risk__prescription__id","ppk")]),
            "relevant.view":forms.widgets.ImgBooleanDisplay(),
            "pre_burn.view":forms.widgets.ImgBooleanDisplay(),
            "day_of_burn.view":forms.widgets.ImgBooleanDisplay(),
            "post_burn.view":forms.widgets.ImgBooleanDisplay(),
            "context_statement.view":forms.widgets.ImgBooleanDisplay(),
            "delete.view":forms.widgets.HyperlinkFactory("id","risk:prescription_action_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
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
        model = Action

class MultipleActionCreateForm(forms.RequestUrlMixin,ActionBaseForm):
    def __init__(self,baseaction,*args,**kwargs):
        kwargs["instance"] = Action(risk=baseaction.risk)
        super().__init__(*args,**kwargs)


    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = Action
        all_fields = ("risk__category","relevant","risk__name","details","pre_burn","day_of_burn","post_burn","context_statement")
        editable_fields = ("relevant","details","pre_burn","day_of_burn","post_burn","context_statement")
        ordered_fields = ("risk__category","relevant","risk__name","details","pre_burn","day_of_burn","post_burn","context_statement")

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

class ActionMemberUpdateForm(ActionCleanMixin,ActionConfigMixin,forms.ListMemberForm):
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
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("risk__category","id","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement","multiple","delete")
        editable_fields = ("id","relevant","details","pre_burn","day_of_burn","post_burn","context_statement")
        ordered_fields = ("id","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement","multiple","delete")

ActionListUpdateForm = forms.listupdateform_factory(ActionMemberUpdateForm,min_num=0,max_num=400,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=False)

class PreburnActionMemberUpdateForm(ActionCleanMixin,ActionConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        pass

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = Action
        widths = {
            "delete":"16px",
        }
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("risk__category","id","relevant","risk_name","details","pre_burn_resolved","pre_burn_explanation","pre_burn_completed","pre_burn_completer","delete")
        editable_fields = ("id","pre_burn_resolved","pre_burn_explanation","pre_burn_completed","pre_burn_completer")
        ordered_fields = ("id","relevant","risk_name","details","pre_burn_resolved","pre_burn_explanation","pre_burn_completed","pre_burn_completer","delete")

PreburnActionListUpdateForm = forms.listupdateform_factory(PreburnActionMemberUpdateForm,min_num=0,max_num=400,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=False)

class DayofburnActionMemberUpdateForm(ActionCleanMixin,ActionConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        pass

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = Action
        widths = {
            "delete":"16px",
        }
        field_required_flag = False
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("risk__category","id","relevant","risk_name","details","day_of_burn_responsible","day_of_burn_include","day_of_burn_situation","day_of_burn_mission","day_of_burn_execution","day_of_burn_administration","day_of_burn_command","day_of_burn_safety","delete")
        editable_fields = ("id","day_of_burn_responsible","day_of_burn_include","day_of_burn_situation","day_of_burn_mission","day_of_burn_execution","day_of_burn_administration","day_of_burn_command","day_of_burn_safety")
        ordered_fields = ("id","relevant","risk_name","details","day_of_burn_responsible","day_of_burn_include","day_of_burn_situation","day_of_burn_mission","day_of_burn_execution","day_of_burn_administration","day_of_burn_command","day_of_burn_safety","delete")

DayofburnActionListUpdateForm = forms.listupdateform_factory(DayofburnActionMemberUpdateForm,min_num=0,max_num=400,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=False)

class PostburnActionMemberUpdateForm(ActionCleanMixin,ActionConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        pass

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = Action
        widths = {
            "delete":"16px",
        }
        field_required_flag = False
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("risk__category","id","relevant","risk_name","details","post_burn_completer","post_burn_completed","delete")
        editable_fields = ("id",)
        ordered_fields = ("id","relevant","risk_name","details","post_burn_completer","post_burn_completed","delete")

PostburnActionListUpdateForm = forms.listupdateform_factory(PostburnActionMemberUpdateForm,min_num=0,max_num=400,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=False)

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
        all_fields = ("risk__category","id","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement")
        editable_fields = []
        ordered_fields = ("id","relevant","risk_name","details","pre_burn","day_of_burn","post_burn","context_statement")

