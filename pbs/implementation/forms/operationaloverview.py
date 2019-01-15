from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (OperationalOverview,)

from dpaw_utils import forms

class OperationalOverviewCleanMixin(object):
    pass

class OperationalOverviewConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "overview":forms.fields.OverrideFieldFactory(OperationalOverview,"overview",field_params={"required":True}),
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "overview.edit":forms.widgets.Textarea(attrs={"class":"vTextField"}),
        }

class OperationalOverviewBaseForm(OperationalOverviewCleanMixin,OperationalOverviewConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class OperationalOverviewUpdateForm(OperationalOverviewBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
    ]
    class Meta:
        model = OperationalOverview
        all_fields = ("overview",)
        editable_fields = ("overview",)


