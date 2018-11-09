from dpaw_utils import forms

from pbs.prescription.models import (Prescription,)


RemoteSensingPriorityDisplay = forms.widgets.ChoiceWidgetFactory("RemoteSensingPriorityDisplay",Prescription.SENSING_PRIORITY_CHOICES)
PlanningStatusDisplay = forms.widgets.ChoiceWidgetFactory("PlanningStatusDisplay",Prescription.PLANNING_CHOICES)
PrescriptionStatusDisplay = forms.widgets.ChoiceWidgetFactory("PrescriptionStatusDisplay",Prescription.STATUS_CHOICES)
IgnitionStatusDisplay = forms.widgets.ChoiceWidgetFactory("IgnitionStatusDisplay",Prescription.IGNITION_STATUS_CHOICES)
ApprovalStatusDisplay = forms.widgets.ChoiceWidgetFactory("ApprovalStatusDisplay",Prescription.APPROVAL_CHOICES)
EndorsementStatusDisplay = forms.widgets.ChoiceWidgetFactory("EndorsementStatusDisplay",Prescription.ENDORSEMENT_CHOICES)
