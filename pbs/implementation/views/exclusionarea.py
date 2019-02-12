from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Treatment,)
from pbs.implementation.models import (ExclusionArea,)
from pbs.implementation.forms import (ExclusionAreaListUpdateForm,ExclusionAreaListForm,)
from pbs.risk.forms import (TreatmentListForm,)
from dpaw_utils import views

import pbs.forms

class PrescriptionExclusionAreaListUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Areas to be Excluded From Ignition"
    pmodel = Prescription
    model = ExclusionArea
    listform_class = ExclusionAreaListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/exclusionarea/"
    urlname = "prescription_exclusionarea_changelist"
    template_name_suffix = "_changelist"
    default_order = ("id",)

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_exclusionarea_changelist",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("implementation:prescription_exclusionareas_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/exclusionarea/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_exclusionarea_delete_confirm'),
            path('prescription/<int:ppk>/exclusionareas/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_exclusionareas_delete'),
        ]

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return ExclusionAreaListForm
        else:
            return super().get_listform_class()

    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["treatmentlistform"] = TreatmentListForm(instance_list=Treatment.objects.filter(register__prescription = self.pobject),request=self.request,requesturl = self.requesturl)

        return context

