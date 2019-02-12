from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Contingency,)
from pbs.risk.forms import (ContingencyCreateForm,ContingencyUpdateForm,ActionMigratedContingencyUpdateForm,NotificationMigratedContingencyUpdateForm,UnmigratedContingencyUpdateForm,ContingencyListForm,ContingencyDeleteListForm)
from dpaw_utils import views

import pbs.forms

class PrescriptionContingencyCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Contingency Plan"
    pmodel = Prescription
    model = Contingency
    form_class = ContingencyCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/contingency/add/"
    urlname = "prescription_contingency_create"
    template_name_suffix = "_create"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.id,))

class PrescriptionContingencyUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Contingency Plan"
    pmodel = Prescription
    model = Contingency
    form_class = ContingencyUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/contingency/<int:pk>/"
    urlname = "prescription_contingency_update"
    template_name_suffix = "_update"

    def get_form_class(self):
        if (self.object.actions_migrated and not self.object.action) and \
            (self.object.notifications_migrated and not self.object.notify_name and not self.object.location and not self.object.organisation and not self.object.contact_number):
            return ContingencyUpdateForm
        elif self.object.actions_migrated and not self.object.action:
            return ActionMigratedContingencyUpdateForm
        elif self.object.notifications_migrated and not self.object.notify_name and not self.object.location and not self.object.organisation and not self.object.contact_number:
            return NotificationMigratedContingencyUpdateForm
        else:
            return UnmigratedContingencyUpdateForm

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.id,))


class PrescriptionContingencyListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Contingency Plan"
    pmodel = Prescription
    model = Contingency
    listform_class = ContingencyListForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/contingency/"
    urlname = "prescription_contingency_list"
    template_name_suffix = "_list"
    default_order = ("description","id")

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:prescription_contingencys_delete",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == "deleteconfirm":
            return ContingencyDeleteListForm
        else:
            return ContingencyListForm

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/contingency/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_contingency_delete_confirm'),
            path('prescription/<int:ppk>/contingencys/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_contingencys_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

