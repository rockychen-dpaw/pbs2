
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from ..models import (RegionalObjective,)

from dpaw_utils import forms

class RegionalObjectiveCleanMixin(object):
    pass

class RegionalObjectiveConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "impact":forms.fields.ChoiceFieldFactory(choices=RegionalObjective.IMPACT_CHOICES),
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "impact.view": forms.widgets.ChoiceWidgetFactory("RegionalObjective.impact",RegionalObjective.IMPACT_CHOICES)
        }

class RegionalObjectiveBaseListForm(RegionalObjectiveConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')

class RegionalObjectiveListForm(RegionalObjectiveBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(RegionalObjectiveListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RegionalObjective
        fields = ("region","impact","fma_names","objectives")
        other_fields = []
        
        editable_fields = []
        ordered_fields = ("region","impact","fma_names","objectives")

