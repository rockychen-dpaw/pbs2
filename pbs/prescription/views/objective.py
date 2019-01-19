from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,Objective)
from pbs.prescription.forms import (ObjectiveListUpdateForm,ObjectiveListForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionObjectivesUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Burn Objectives"
    pmodel = Prescription
    model = Objective
    listform_class = ObjectiveListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/objective/"
    urlname = "prescription_objective_changelist"

    @property
    def deleteconfirm_url(self):
        return urls.reverse("prescription:prescription_objectives_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/objective/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_objective_delete_confirm'),
            path('prescription/<int:ppk>/objectives/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_objectives_delete'),
        ]

    def _get_success_url(self):
        return urls.reverse("prescription:prescription_objective_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return ObjectiveListForm
        else:
            return super().get_listform_class()


