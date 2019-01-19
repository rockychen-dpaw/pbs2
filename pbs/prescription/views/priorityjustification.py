from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,PriorityJustification)
from pbs.prescription.forms import (PriorityJustificationListUpdateForm,PriorityJustificationListForm,PrescriptionPriorityUpdateForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionPriorityJustificationsUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Burn Priority Justification"
    pmodel = Prescription
    model = PriorityJustification
    pform_class = PrescriptionPriorityUpdateForm
    context_pform_name = "prescriptionform"
    listform_class = PriorityJustificationListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/priorityjustification/"
    urlname = "prescription_priorityjustification_changelist"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(relevant=True)
        return qs


    def get_ordering(self):
        return "order"

    @property
    def deleteconfirm_url(self):
        return urls.reverse("prescription:prescription_priorityjustifications_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/priorityjustification/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_priorityjustification_delete_confirm'),
            path('prescription/<int:ppk>/priorityjustifications/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_priorityjustifications_delete'),
        ]

    def _get_success_url(self):
        return urls.reverse("prescription:prescription_priorityjustification_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return PriorityJustificationListForm
        else:
            return super().get_listform_class()

