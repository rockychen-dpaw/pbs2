from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.prescription.forms import (PrescriptionMaximumDraftRiskForm,)
from pbs.risk.models import (Register,factorlist)
from pbs.risk.forms import (RegisterListUpdateForm,RegisterListForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionRegistersUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Prescribed Burn Risk Register"
    pmodel = Prescription
    model = Register
    pform_class = PrescriptionMaximumDraftRiskForm
    listform_class = RegisterListUpdateForm
    context_pform_name = "prescriptionform"
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/register/"
    urlname = "prescription_register_changelist"
    filtertool = False


    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:prescription_registers_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/register/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_register_delete_confirm'),
            path('prescription/<int:ppk>/registers/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_registers_delete'),
        ]

    def get_success_url(self):
        return urls.reverse("risk:prescription_register_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return RegisterListForm
        else:
            return super().get_listform_class()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["factorlist"] = factorlist

        return context
