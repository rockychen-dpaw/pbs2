from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.implementation.models import (OperationalOverview,)
from pbs.implementation.forms import (OperationalOverviewUpdateForm,)
from dpaw_utils.views import (OneToOneUpdateView,)

class PrescriptionOperationalOverviewUpdateView(OneToOneUpdateView):
    title = "Operational Overview"
    pmodel = Prescription
    model = OperationalOverview
    form_class = OperationalOverviewUpdateForm
    context_pobject_name = "prescription"
    one_to_one_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/operationaloverview/"
    urlname = "prescription_operationaloverview_update"
    template_name_suffix = "_update"

    def get_success_url(self):
        return urls.reverse("implementation:prescription_operationaloverview_update",args=(self.pobject.id,))
    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

