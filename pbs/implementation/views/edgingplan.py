from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Treatment,)
from pbs.implementation.models import (EdgingPlan,)
from pbs.implementation.forms import (EdgingPlanCreateForm,EdgingPlanUpdateForm,EdgingPlanListForm,)
from pbs.risk.forms import (TreatmentListForm,)
from dpaw_utils import views

import pbs.forms

class PrescriptionEdgingPlanCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Edging Plan"
    pmodel = Prescription
    model = EdgingPlan
    form_class = EdgingPlanCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/edgingplan/add/"
    urlname = "prescription_edgingplan_create"
    template_name_suffix = "_create"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_edgingplan_list",args=(self.pobject.id,))

class PrescriptionEdgingPlanUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Edging Plan"
    pmodel = Prescription
    model = EdgingPlan
    form_class = EdgingPlanUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/edgingplan/<int:pk>/"
    urlname = "prescription_edgingplan_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_edgingplan_list",args=(self.pobject.id,))


class PrescriptionEdgingPlanListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Edging Plan"
    pmodel = Prescription
    model = EdgingPlan
    listform_class = EdgingPlanListForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/edgingplan/"
    urlname = "prescription_edgingplan_list"
    template_name_suffix = "_list"
    default_order = ("location","fuel_type__name","id")

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_edgingplan_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("implementation:prescription_edgingplans_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/edgingplan/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_edgingplan_delete_confirm'),
            path('prescription/<int:ppk>/edgingplans/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_edgingplans_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)

    def update_context_data(self,context):
        super().update_context_data(context)
    """

