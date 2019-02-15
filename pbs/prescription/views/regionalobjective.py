
from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,RegionalObjective)
from pbs.prescription.forms import (RegionalObjectiveListForm,)
from dpaw_utils import views
import pbs.forms

class PrescriptionRegionalObjectivesUpdateView(pbs.forms.GetActionMixin,views.ManyToManyListView):
    title = "Select Regional Fire Management Plan Objectives"
    pmodel = Prescription
    model = RegionalObjective
    listform_class = RegionalObjectiveListForm
    context_pobject_name = "prescription"
    many_to_many_field_name = "regional_objectives"
    related_field_name = "prescription"
    urlpattern = "/prescription/<int:ppk>/add/regionalobjectives/"
    urlname = "prescription_regionalobjectives_update"
    template_name_suffix = "_list"

    @property
    def deleteconfirm_url(self):
        return urls.reverse("prescription:prescription_regionalobjectives_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/regionalobjective/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_regionalobjective_delete_confirm'),
            path('prescription/<int:ppk>/regionalobjectives/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_regionalobjectives_delete'),
        ]

    def _get_success_url(self):
        return urls.reverse("risk:context_update",args=(self.pobject.id,))

    def update_context_data(self,context):
        super().update_context_data(context)
        qs = self.model.objects.filter(region=self.pobject.region.id).exclude(prescription=self.pobject)
        context["unselectedlistform"] = self.get_listform_class()(instance_list=qs,request=self.request,requesturl = self.requesturl)
        context["object_list_length"] = len(qs) + len(self.object_list)

