from dpaw_utils.forms.fields import ConditionalMultipleFieldFactory,ChoiceFieldFactory

from pbs.prescription.models import (Prescription,)

PrescriptionCorporateApprovalStatus = ConditionalMultipleFieldFactory(Prescription,"planning_status",("planning_status_modified",),
    view_layouts=[
        (lambda f:f.value() == Prescription.PLANNING_APPROVED,('<span class="badge badge-success"><i class="icon-ok"></i> approved on {0}</span>',("planning_status_modified",),False)),
        (lambda f:f.value() == Prescription.PLANNING_SUBMITTED,('<span class="badge badge-warning"><i class="icon-minus"></i> submitted on {0}</span>',("planning_status_modified",),False)),
        (lambda f:True,('<span class="badge badge-important"><i class="icon-minus"></i> draft</span>',None,False))
    ]
)

PrescriptionEndorsementStatus = ConditionalMultipleFieldFactory(Prescription,"endorsement_status",("endorsement_status_modified",),
    view_layouts=[
        (lambda f:f.value() == Prescription.ENDORSEMENT_APPROVED,('<span class="badge badge-success"><i class="icon-ok"></i> endorsed on {0}</span>',("endorsement_status_modified",),False)),
        (lambda f:f.value() == Prescription.ENDORSEMENT_SUBMITTED,('<span class="badge badge-warning"><i class="icon-minus"></i> submitted on {0}</span>',("endorsement_status_modified",),False)),
        (lambda f:True,('<span class="badge badge-important"><i class="icon-minus"></i> draft</span>',None,False))
    ]
)

PrescriptionApprovalStatus = ConditionalMultipleFieldFactory(Prescription,"approval_status",("current_approval_approver","current_approval_valid_period","approval_status_modified",),
    view_layouts=[
        (lambda f:f.value() == Prescription.APPROVAL_APPROVED,("""
          <span class="badge badge-success">
              <i class="icon-ok" style="display:inline-block; vertical-align:top;"></i>
              <span style="display:inline-block;">
              Approved by {0} <br />
              until {1} <br />
              on {2}
              </span>
          </span>
        """,("current_approval_approver","current_approval_valid_period","approval_status_modified"),False)),
        (lambda f:f.value() == Prescription.APPROVAL_SUBMITTED,('<span class="badge badge-warning"><i class="icon-minus"></i>submitted on {0}</span>',("approval_status_modified",),False)),
        (lambda f:True,('<span class="badge badge-important"><i class="icon-minus"></i> not approved</span>',None,False))
    ]
)

PrescriptionIgnitionCommenceStatus = ConditionalMultipleFieldFactory(Prescription,"ignition_status",("ignition_commenced_date",),
    view_layouts=[
        (lambda f:f.value() != Prescription.IGNITION_NOT_STARTED,('<span class="badge badge-success"><i class="icon-ok"></i> {0}</span>',("ignition_commenced_date",),False)),
        (lambda f:True,('<span class="badge badge-important"><i class="icon-minus"></i>',None,False))
    ]
)

PrescriptionIgnitionCompleteStatus = ConditionalMultipleFieldFactory(Prescription,"ignition_status",("ignition_completed_date",),
    view_layouts=[
        (lambda f:f.value() == Prescription.IGNITION_COMPLETE,('<span class="badge badge-success"><i class="icon-ok"></i> {0}</span>',("ignition_completed_date",),False)),
        (lambda f:True,('<span class="badge badge-important"><i class="icon-minus"></i></span>',None,False))
    ]
)

