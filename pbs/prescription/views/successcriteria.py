from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,SuccessCriteria)
from pbs.prescription.forms import (SuccessCriteriaListUpdateForm,SuccessCriteriaListForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionSuccessCriteriasUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Burn SuccessCriterias"
    pmodel = Prescription
    model = SuccessCriteria
    listform_class = SuccessCriteriaListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/successcriteria/"
    urlname = "prescription_successcriteria_changelist"

    @property
    def deleteconfirm_url(self):
        return urls.reverse("prescription:prescription_successcriterias_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/successcriteria/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_successcriteria_delete_confirm'),
            path('prescription/<int:ppk>/successcriterias/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_successcriterias_delete'),
        ]

    def get_success_url(self):
        return urls.reverse("prescription:prescription_successcriteria_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return SuccessCriteriaListForm
        else:
            return super().get_listform_class()


