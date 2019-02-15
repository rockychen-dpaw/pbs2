from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Treatment,)
from pbs.implementation.models import (BurningPrescription,)
from pbs.implementation.forms import (BurningPrescriptionCreateForm,BurningPrescriptionUpdateForm,BurningPrescriptionListForm,)
from pbs.risk.forms import (TreatmentListForm,)
from dpaw_utils import views

import pbs.forms

class PrescriptionBurningPrescriptionCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Burning Prescription"
    pmodel = Prescription
    model = BurningPrescription
    form_class = BurningPrescriptionCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/burningprescription/add/"
    urlname = "prescription_burningprescription_create"
    template_name_suffix = "_create"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_burningprescription_list",args=(self.pobject.id,))

class PrescriptionBurningPrescriptionUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Burning Prescription"
    pmodel = Prescription
    model = BurningPrescription
    form_class = BurningPrescriptionUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/burningprescription/<int:pk>/"
    urlname = "prescription_burningprescription_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_burningprescription_list",args=(self.pobject.id,))


class PrescriptionBurningPrescriptionListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Burning Prescriptions"
    pmodel = Prescription
    model = BurningPrescription
    listform_class = BurningPrescriptionListForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/burningprescription/"
    urlname = "prescription_burningprescription_list"
    template_name_suffix = "_list"
    default_order = ("fuel_type__name","id")

    def get_mediaforms(self):
        return (self.get_listform_class(),TreatmentListForm)

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_burningprescription_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("implementation:prescription_burningprescriptions_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/burningprescription/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_burningprescription_delete_confirm'),
            path('prescription/<int:ppk>/burningprescriptions/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_burningprescriptions_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

    def update_context_data(self,context):
        super().update_context_data(context)
        context["treatmentlistform"] = TreatmentListForm(instance_list=Treatment.objects.filter(register__prescription = self.pobject),request=self.request,requesturl = self.requesturl)
        context["documents_165"] = self.pobject.document_set.filter(tag__id=165)
        context["documents_167"] = self.pobject.document_set.filter(tag__id=167)

