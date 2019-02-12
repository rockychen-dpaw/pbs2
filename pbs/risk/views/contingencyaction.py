from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (ContingencyAction,Contingency)
from pbs.risk.forms import (ContingencyActionCreateForm,ContingencyActionUpdateForm,ContingencyActionListForm)
from dpaw_utils import views

import pbs.forms

class ContingencyActionCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Contingency Action"
    pmodel = Contingency
    model = ContingencyAction
    form_class = ContingencyActionCreateForm
    context_pobject_name = "contingency"
    one_to_many_field_name = "contingency"
    urlpattern = "contingency/<int:ppk>/action/add/"
    urlname = "contingency_action_create"
    template_name_suffix = "_create"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.prescription.id,))

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["prescription"] = self.pobject.prescription

        return context

class ContingencyActionUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Contingency Action"
    pmodel = Contingency
    model = ContingencyAction
    form_class = ContingencyActionUpdateForm
    context_pobject_name = "contingency"
    one_to_many_field_name = "contingency"
    urlpattern = "contingency/<int:ppk>/action/<int:pk>/"
    urlname = "contingency_action_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.prescription.id,))

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["prescription"] = self.pobject.prescription

        return context


class ContingencyActionListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Contingency Action"
    pmodel = Contingency
    model = ContingencyAction
    listform_class = ContingencyActionListForm
    context_pobject_name = "contingency"
    one_to_many_field_name = "contingency"
    urlpattern = "contingency/<int:ppk>/action/"
    urlname = "contingency_action_list"
    template_name_suffix = "_list"
    default_order = ("action","id")

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:contingency_actions_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('contingency/<int:ppk>/action/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='contingency_action_delete_confirm'),
            path('contingency/<int:ppk>/actions/delete', cls.as_view(),{"action":"deleteconfirmed"},name='contingency_actions_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["prescription"] = self.pobject.prescription

        return context


    def get_deleteconfirm_context(self):
        context = super().get_deleteconfirm_context()
        context["prescription"] = self.pobject.prescription

        return context
