from django.urls import path 
from django import urls
from django.db import transaction

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Action,Risk)
from pbs.risk.forms import (CustomRiskCreateForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionRiskCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Potential Sources of Risk"
    pmodel = Prescription
    model = Risk
    form_class = CustomRiskCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/risk/"
    urlname = "prescription_risk_create"
    template_name_suffix = "_create"

    def get_success_url(self):
        return urls.reverse("risk:prescription_action_changelist",args=(self.object.prescription.id,))

    def form_valid(self,form):
        with transaction.atomic():
            result = super().form_valid(form)
            Action(risk = form.instance,relevant=True,index = 1,total = 1).save()
            return result
        

