
from dpaw_utils import forms
from dpaw_utils import utils

from pbs.prescription.models import (Prescription,FundingAllocation)
from pbs.risk.models import (Register,Complexity)


RemoteSensingPriorityDisplay = forms.widgets.ChoiceWidgetFactory("RemoteSensingPriorityDisplay",Prescription.SENSING_PRIORITY_CHOICES)
PlanningStatusDisplay = forms.widgets.ChoiceWidgetFactory("PlanningStatusDisplay",Prescription.PLANNING_CHOICES)
PrescriptionStatusDisplay = forms.widgets.ChoiceWidgetFactory("PrescriptionStatusDisplay",Prescription.STATUS_CHOICES)
IgnitionStatusDisplay = forms.widgets.ChoiceWidgetFactory("IgnitionStatusDisplay",Prescription.IGNITION_STATUS_CHOICES)
ApprovalStatusDisplay = forms.widgets.ChoiceWidgetFactory("ApprovalStatusDisplay",Prescription.APPROVAL_CHOICES)
EndorsementStatusDisplay = forms.widgets.ChoiceWidgetFactory("EndorsementStatusDisplay",Prescription.ENDORSEMENT_CHOICES)

IgnitionTypeDisplay = forms.widgets.ChoiceWidgetFactory("IgnitionTypeDisplay",{
    True:"Aerial",
    False:"Ground",
    None:""
})

RiskLevelDisplay = forms.widgets.ChoiceWidgetFactory("RiskLevelDisplay",{
    Register.LEVEL_VERY_LOW:'<span class="label label-very-low">{}</span>'.format(Register.LEVEL_CHOICES[Register.LEVEL_VERY_LOW - 1][1]),
    Register.LEVEL_LOW:'<span class="label label-low">{}</span>'.format(Register.LEVEL_CHOICES[Register.LEVEL_LOW - 1][1]),
    Register.LEVEL_MEDIUM:'<span class="label label-medium">{}</span>'.format(Register.LEVEL_CHOICES[Register.LEVEL_MEDIUM - 1][1]),
    Register.LEVEL_HIGH:'<span class="label label-high">{}</span>'.format(Register.LEVEL_CHOICES[Register.LEVEL_HIGH - 1][1]),
    Register.LEVEL_VERY_HIGH:'<span class="label label-very-high">{}</span>'.format(Register.LEVEL_CHOICES[Register.LEVEL_VERY_HIGH - 1][1]),
    "__default__":'<span class="label label-very-high">{}</span>'.format(Register.LEVEL_CHOICES[Register.LEVEL_VERY_HIGH - 1][1])
},marked_safe=True)

RiskRoleDisplay = forms.widgets.ChoiceWidgetFactory("RiskRoleDisplay",{
    Register.LEVEL_VERY_LOW:'<span class="label label-very-low">District Manager</span>',
    Register.LEVEL_LOW:'<span class="label label-low">District Manager</span>',
    Register.LEVEL_MEDIUM:'<span class="label label-medium">Regional Manager</span>',
    Register.LEVEL_HIGH:'<span class="label label-high">Branch Manager FMSB</span>',
    Register.LEVEL_VERY_HIGH:'<span class="label label-very-high">Not available(the risk level is too high)</span>',
    "__default__":'<span class="label label-very-high">Not available(the risk level is too high)</span>'
},marked_safe=True)


ComplexityRatingDisplay = forms.widgets.ChoiceWidgetFactory("ComplexityRatingDisplay",{
    Complexity.RATING_UNRATED:'<span class="label label-unrated">{}</span>'.format(Complexity.RATING_CHOICES[Complexity.RATING_UNRATED][1]),
    Complexity.RATING_LOW:'<span class="label label-low">{}</span>'.format(Complexity.RATING_CHOICES[Complexity.RATING_LOW - 1][1]),
    Complexity.RATING_MEDIUM:'<span class="label label-medium">{}</span>'.format(Complexity.RATING_CHOICES[Complexity.RATING_MEDIUM - 1][1]),
    Complexity.RATING_HIGH:'<span class="label label-high">{}</span>'.format(Complexity.RATING_CHOICES[Complexity.RATING_HIGH - 1][1]),
},marked_safe=True)

PrescriptionPriorityDisplay = forms.widgets.ChoiceWidgetFactory("PrescriptionPriorityDisplay",Prescription.PRIORITY_CHOICES)


StateProgressBarDisplay = forms.widgets.ChoiceWidgetFactory("StateProgressBarDisplay",utils.RangeChoice([
    (33,"""<div class="progress progress-danger">{0}%<div class="bar" style="width: {0}%;"></div></div>"""),
    (50,"""<div class="progress progress-warning">{0}%<div class="bar" style="width: {0}%;"></div></div>"""),
    (66,"""<div class="progress progress-warning"><div class="bar" style="width: {0}%;">{0}%</div></div>"""),
    (None,"""<div class="progress progress-success"><div class="bar" style="width: {0}%;">{0}%</div></div>"""),

]),marked_safe=True,template=True)

PrescriptionStatusIconDisplay = forms.widgets.ChoiceWidgetFactory("PrescriptionStatusIconDisplay",{
    Prescription.STATUS_OPEN:"""<span class="badge badge-important"><i class="icon-minus"></i></span>""",
    Prescription.STATUS_CLOSED:"""<span class="badge badge-success"><i class="icon-ok"></i></span>""",
    "__default__":''

},marked_safe=True,template=True)


CompleteStatusDisplay = forms.widgets.ChoiceWidgetFactory("CompleteStatusDisplay",{
    True:"Complete",
    False:"Incomplete",
    None:""
})

FundingAllocationDisplay = forms.widgets.ChoiceWidgetFactory("FundingAllocationDisplay",FundingAllocation.ALLOCATION_CHOICES)

