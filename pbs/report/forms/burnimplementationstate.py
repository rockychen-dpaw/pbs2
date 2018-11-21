from django.utils import timezone

from dpaw_utils import forms

from pbs.report.models import (BurnImplementationState,)
from pbs.forms import (FORM_ACTIONS,LIST_ACTIONS)
from pbs.utils import FinancialYear
import pbs.widgets


class BurnImplementationStateCleanMixin(object):
    pass

class BurnImplementationStateConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "progress":pbs.widgets.StateProgressBarDisplay,

        }

class BurnImplementationStateBaseForm(BurnImplementationStateCleanMixin,BurnImplementationStateConfigMixin,forms.ModelForm):
    class Meta:
        pass

class BurnImplementationStateViewForm(BurnImplementationStateBaseForm):
    all_actions = [
    ]
    def __init__(self, *args, **kwargs):
        super(BurnImplementationStateViewForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BurnImplementationState
        purpose = "view"
        fields = []
        other_fields = ('progress',)
