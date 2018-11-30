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
            "post_actions.view":pbs.widgets.CompleteStatusDisplay(),
            "post_actions.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "evaluation_summary.view":pbs.widgets.CompleteStatusDisplay(),
            "evaluation_summary.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "evaluation.view":pbs.widgets.CompleteStatusDisplay(),
            "evaluation.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "post_ignitions.view":pbs.widgets.CompleteStatusDisplay(),
            "post_ignitions.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "aerial_intensity.view":pbs.widgets.CompleteStatusDisplay(),
            "aerial_intensity.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "satellite_intensity.view":pbs.widgets.CompleteStatusDisplay(),
            "satellite_intensity.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "other.view":pbs.widgets.CompleteStatusDisplay(),
            "other.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "post_burn_checklist.view":pbs.widgets.CompleteStatusDisplay(),
            "post_burn_checklist.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "closure_declaration.view":pbs.widgets.CompleteStatusDisplay(),
            "closure_declaration.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "signage.view":pbs.widgets.CompleteStatusDisplay(),
            "signage.edit":forms.widgets.Select(attrs={"onchange":"submit_post_state(this)"}),
            "progress":pbs.widgets.StateProgressBarDisplay,

        }

class BurnClosureStateBaseForm(BurnClosureStateCleanMixin,BurnClosureStateConfigMixin,forms.ModelForm):
    class Meta:
        pass

class BurnClosureStateViewForm(BurnClosureStateBaseForm):
    all_actions = [
    ]

    class Meta:
        model = BurnClosureState
        purpose = "view"
        fields = ["post_actions","evaluation_summary","evaluation","post_ignitions","aerial_intensity","satellite_intensity","other","post_burn_checklist","closure_declaration","signage"]
        other_fields = ('progress',)

class BurnClosureStateUpdateForm(forms.EditableFieldsMixin,BurnClosureStateBaseForm):
    all_actions = [
    ]

    class Meta:
        model = BurnClosureState
        fields = ["post_actions","evaluation_summary","evaluation","post_ignitions","aerial_intensity","satellite_intensity","other","post_burn_checklist","closure_declaration","signage"]
        editable_fields = fields
