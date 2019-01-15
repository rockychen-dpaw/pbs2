from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.prescription.forms import (PrescriptionMaximumDraftRiskForm,)
from pbs.risk.models import (Complexity,factorlist)
from pbs.risk.forms import (ComplexityListUpdateForm,ComplexityListForm,ComplexityFilterForm)
from pbs.risk.filters import (ComplexityFilter,)
from dpaw_utils import views
import pbs.forms

class PrescriptionComplexitiesUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Prescribed Burn Complexity Analysis Summary"
    pmodel = Prescription
    model = Complexity
    filter_class = ComplexityFilter
    filterform_class = ComplexityFilterForm
    pform_class = PrescriptionMaximumDraftRiskForm
    listform_class = ComplexityListUpdateForm
    context_pform_name = "prescriptionform"
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/complexity/"
    urlname = "prescription_complexity_changelist"
    filtertool = False


    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:prescription_complexities_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/complexity/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_complexity_delete_confirm'),
            path('prescription/<int:ppk>/complexities/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_complexities_delete'),
        ]

    def get_success_url(self):
        return urls.reverse("risk:prescription_complexity_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return ComplexityListForm
        else:
            return super().get_listform_class()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["factorlist"] = factorlist

        return context
