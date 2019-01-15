from django.utils import timezone

from dpaw_utils import forms

from pbs.report.models import (SummaryCompletionState,)
from pbs.utils import FinancialYear
import pbs.widgets


class SummaryCompletionStateCleanMixin(object):
    pass

class SummaryCompletionStateConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "summary.view":pbs.widgets.CompleteStatusDisplay(),
            "summary.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "context_statement.view":pbs.widgets.CompleteStatusDisplay(),
            "context_statement.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "context_map.view":pbs.widgets.CompleteStatusDisplay(),
            "context_map.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "objectives.view":pbs.widgets.CompleteStatusDisplay(),
            "objectives.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "success_criteria.view":pbs.widgets.CompleteStatusDisplay(),
            "success_criteria.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "priority_justification.view":pbs.widgets.CompleteStatusDisplay(),
            "priority_justification.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "complexity_analysis.view":pbs.widgets.CompleteStatusDisplay(),
            "complexity_analysis.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "risk_register.view":pbs.widgets.CompleteStatusDisplay(),
            "risk_register.edit":forms.widgets.Select(attrs={"onchange":"submit_pre_state(this)"}),
            "progress.view":pbs.widgets.StateProgressBarDisplay,

        }

class SummaryCompletionStateBaseForm(SummaryCompletionStateCleanMixin,SummaryCompletionStateConfigMixin,forms.ModelForm):
    class Meta:
        pass

class SummaryCompletionStateViewForm(SummaryCompletionStateBaseForm):

    class Meta:
        model = SummaryCompletionState
        purpose = (None,"view")
        all_fields = ["summary","context_statement","context_map","objectives","success_criteria","priority_justification","complexity_analysis","risk_register",'progress']


class SummaryCompletionStateUpdateForm(forms.EditableFieldsMixin,SummaryCompletionStateBaseForm):

    class Meta:
        model = SummaryCompletionState
        all_fields = ["summary","context_statement","context_map","objectives","success_criteria","priority_justification","complexity_analysis","risk_register"]
        editable_fields = all_fields
