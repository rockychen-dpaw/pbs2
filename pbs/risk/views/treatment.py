from django.urls import path 
from django import urls
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import (HttpResponseRedirect,)

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Action,Treatment)
from pbs.risk.forms import (TreatmentDetailForm,TreatmentListForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionTreatmentDetailView(pbs.forms.GetActionMixin,views.RequestActionMixin,views.OneToManyDetailView):
    title = "View Treatment"
    pmodel = Prescription
    model = Treatment
    form_class = TreatmentDetailForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "register__prescription"
    urlpattern = "prescription/<int:ppk>/treatment/<int:pk>"
    urlname = "prescription_treatment_detail"
    template_name_suffix = "_detail"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_treatment_detail",args=(self.pobject.id,self.object.id))

    @classmethod
    def _get_extra_urlpatterns(cls):
        return [
            path('prescription/<int:ppk>/treatment/<int:pk>/setcomplete', csrf_exempt(cls.as_view()),{'action':'set_complete'},name='prescription_treatment_complete_set')
        ]

    def set_complete_ajax(self):
        complete = TreatmentListForm.base_fields["complete"].to_python(self.request.POST.get("value"))
        self.object.complete = complete
        self.object.save(update_fields=["complete","modifier","modified"])
        



