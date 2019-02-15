from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.prescription.models import (BriefingChecklist,)

from dpaw_utils import forms

class BriefingChecklistCleanMixin(object):
    pass

class BriefingChecklistConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(BriefingChecklist,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(BriefingChecklist,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_briefingchecklist_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<img title='Delete' onclick='window.location=\"{url}\"' src='/static/img/delete.png' style='width:16px;height:16px;cursor:pointer'>")
        }

class BriefingChecklistBaseForm(BriefingChecklistCleanMixin,BriefingChecklistConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.contingency = parent_instance

    class Meta:
        pass

class BriefingChecklistUpdateForm(BriefingChecklistBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = BriefingChecklist
        purpose = ("edit","view")
        all_fields = ("title","notes")
        editable_fields = ("title","notes")

class BriefingChecklistBaseListForm(BriefingChecklistConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class BriefingChecklistListForm(BriefingChecklistBaseListForm):
    class Meta:
        model = BriefingChecklist
        all_fields = ("smeac","title","notes","delete")
        widths = {
            "delete":"16px",
        }
        editable_fields = []

