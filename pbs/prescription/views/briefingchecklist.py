from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,BriefingChecklist,)
from pbs.prescription.forms import (BriefingChecklistUpdateForm,BriefingChecklistListForm,)
from dpaw_utils import views

import pbs.forms

class PrescriptionBriefingChecklistUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Breifing Checklist"
    pmodel = Prescription
    model = BriefingChecklist
    form_class = BriefingChecklistUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/briefingchecklist/<int:pk>/"
    urlname = "prescription_briefingchecklist_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_briefingchecklist_list",args=(self.pobject.id,))


class PrescriptionBriefingChecklistListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Briefing Checklist"
    pmodel = Prescription
    model = BriefingChecklist
    listform_class = BriefingChecklistListForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/briefingchecklist/"
    urlname = "prescription_briefingchecklist_list"
    template_name_suffix = "_list"
    default_order = ("smeac","id")

    def _get_success_url(self):
        return urls.reverse("prescription:prescription_briefingchecklist_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("prescription:prescription_briefingchecklists_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/briefingchecklist/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_briefingchecklist_delete_confirm'),
            path('prescription/<int:ppk>/briefingchecklists/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_briefingchecklists_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """
    def update_context_data(self,context):
        super().update_context_data(context)
        context["documents"] = self.pobject.document_set.filter(tag__id=182)

