from django.utils import timezone

from dpaw_utils import forms

from pbs.report.models import (BurnClosureState,)
from pbs.forms import (FORM_ACTIONS,LIST_ACTIONS)
from pbs.utils import FinancialYear
import pbs.widgets


class BurnClosureStateCleanMixin(object):
    pass

class BurnClosureStateConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "progress":pbs.widgets.StateProgressBarDisplay,

        }

class BurnClosureStateBaseForm(BurnClosureStateCleanMixin,BurnClosureStateConfigMixin,forms.ModelForm):
    class Meta:
        pass

class BurnClosureStateViewForm(BurnClosureStateBaseForm):
    all_actions = [
    ]
    def __init__(self, *args, **kwargs):
        super(BurnClosureStateViewForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BurnClosureState
        purpose = "view"
        fields = []
        other_fields = ('progress',)
