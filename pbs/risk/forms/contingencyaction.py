from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (ContingencyAction,)

from dpaw_utils import forms

class ContingencyActionCleanMixin(object):
    pass

class ContingencyActionConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(ContingencyAction,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(ContingencyAction,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            'action.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            "action.list":forms.widgets.HyperlinkFactory("action","risk:contingency_action_update",ids=[("id","pk"),("contingency","ppk")]),
            "delete.view":forms.widgets.HyperlinkFactory("id","risk:contingency_action_delete_confirm",ids=[("id","pk"),("contingency","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<img title='Delete' onclick='window.location=\"{url}\"' src='/static/img/inlinedelete.png' style='width:12px;height:12px;cursor:pointer'>")
        }

class ContingencyActionBaseForm(ContingencyActionCleanMixin,ContingencyActionConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.contingency = parent_instance

    class Meta:
        pass

class ContingencyActionCreateForm(ContingencyActionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = ContingencyAction
        purpose = ("edit","view")
        all_fields = ("action",)
        editable_fields = all_fields

class ContingencyActionUpdateForm(ContingencyActionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = ContingencyAction
        purpose = ("edit","view")
        all_fields = ("action",)
        editable_fields = ("action",)

class ContingencyActionBaseListForm(ContingencyActionConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ContingencyActionListForm(ContingencyActionBaseListForm):
    class Meta:
        model = ContingencyAction
        all_fields = ("action","delete")
        widths = {
            "delete":"16px",
        }
        editable_fields = []

class ContingencyActionListOnlyForm(ContingencyActionBaseListForm):
    class Meta:
        model = ContingencyAction
        purpose = (None,('listonly','view'))
        all_fields = ("action",)
        editable_fields = []

