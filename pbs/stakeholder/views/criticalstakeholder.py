from django import urls

from pbs.prescription.models import (Prescription,)
from ..models import (CriticalStakeholder,)
from ..forms import (CriticalStakeholderListUpdateForm,)
from dpaw_utils.views import (OneToManyListUpdateView,)

class CriticalStakeholderListUpdateView(OneToManyListUpdateView):
    model=CriticalStakeholder
    listform_class = CriticalStakeholderListUpdateForm
    urlpattern = "criticalstakeholder/prescription/<int:ppk>/"
    urlname = "{}_changelist"
    one_to_many_field_name = "prescription"
    pmodel = Prescription
    ppk_url_kwarg = "ppk"
    context_pobject_name = "prescription"



