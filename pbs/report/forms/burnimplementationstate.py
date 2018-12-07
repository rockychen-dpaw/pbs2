from django.utils import timezone

from dpaw_utils import forms

from pbs.report.models import (BurnImplementationState,)
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
            "overview.view":pbs.widgets.CompleteStatusDisplay(),
            "overview.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "pre_actions.view":pbs.widgets.CompleteStatusDisplay(),
            "pre_actions.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "actions.view":pbs.widgets.CompleteStatusDisplay(),
            "actions.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "roads.view":pbs.widgets.CompleteStatusDisplay(),
            "roads.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "traffic.view":pbs.widgets.CompleteStatusDisplay(),
            "traffic.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "tracks.view":pbs.widgets.CompleteStatusDisplay(),
            "tracks.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "burning_prescription.view":pbs.widgets.CompleteStatusDisplay(),
            "burning_prescription.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "fuel_assessment.view":pbs.widgets.CompleteStatusDisplay(),
            "fuel_assessment.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "edging_plan.view":pbs.widgets.CompleteStatusDisplay(),
            "edging_plan.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "contingency_plan.view":pbs.widgets.CompleteStatusDisplay(),
            "contingency_plan.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "lighting_sequence.view":pbs.widgets.CompleteStatusDisplay(),
            "lighting_sequence.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "exclusion_areas.view":pbs.widgets.CompleteStatusDisplay(),
            "exclusion_areas.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "organisational_structure.view":pbs.widgets.CompleteStatusDisplay(),
            "organisational_structure.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "briefing.view":pbs.widgets.CompleteStatusDisplay(),
            "briefing.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "operation_maps.view":pbs.widgets.CompleteStatusDisplay(),
            "operation_maps.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "aerial_maps.view":pbs.widgets.CompleteStatusDisplay(),
            "aerial_maps.edit":forms.widgets.Select(attrs={"onchange":"submit_day_state(this)"}),
            "progress.view":pbs.widgets.StateProgressBarDisplay,
        }

class BurnImplementationStateBaseForm(BurnImplementationStateCleanMixin,BurnImplementationStateConfigMixin,forms.ModelForm):
    class Meta:
        pass

class BurnImplementationStateViewForm(BurnImplementationStateBaseForm):

    class Meta:
        model = BurnImplementationState
        purpose = "view"
        fields = ["overview","pre_actions","actions","roads","traffic","tracks","burning_prescription","fuel_assessment","edging_plan","contingency_plan","lighting_sequence",
                "exclusion_areas","organisational_structure","briefing","operation_maps","aerial_maps"]
        other_fields = ('progress',)


class BurnImplementationStateUpdateForm(forms.EditableFieldsMixin,BurnImplementationStateBaseForm):

    class Meta:
        model = BurnImplementationState
        fields = ["overview","pre_actions","actions","roads","traffic","tracks","burning_prescription","fuel_assessment","edging_plan","contingency_plan","lighting_sequence",
                "exclusion_areas","organisational_structure","briefing","operation_maps","aerial_maps"]
        editable_fields = fields
