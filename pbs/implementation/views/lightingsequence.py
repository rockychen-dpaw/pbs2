from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.implementation.models import (LightingSequence,)
from pbs.implementation.forms import (LightingSequenceCreateForm,LightingSequenceUpdateForm,LightingSequenceListForm,)
from dpaw_utils import views

import pbs.forms

class PrescriptionLightingSequenceCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Lighting Sequence"
    pmodel = Prescription
    model = LightingSequence
    form_class = LightingSequenceCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/lightingsequence/add/"
    urlname = "prescription_lightingsequence_create"
    template_name_suffix = "_create"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_lightingsequence_list",args=(self.pobject.id,))

class PrescriptionLightingSequenceUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Lighting Sequence"
    pmodel = Prescription
    model = LightingSequence
    form_class = LightingSequenceUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/lightingsequence/<int:pk>/"
    urlname = "prescription_lightingsequence_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_lightingsequence_list",args=(self.pobject.id,))


class PrescriptionLightingSequenceListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Lighting Sequence"
    pmodel = Prescription
    model = LightingSequence
    listform_class = LightingSequenceListForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/lightingsequence/"
    urlname = "prescription_lightingsequence_list"
    template_name_suffix = "_list"
    default_order = ("seqno","id")

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_lightingsequence_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("implementation:prescription_lightingsequences_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/lightingsequence/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_lightingsequence_delete_confirm'),
            path('prescription/<int:ppk>/lightingsequences/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_lightingsequences_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

