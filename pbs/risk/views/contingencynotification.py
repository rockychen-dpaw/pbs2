from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (ContingencyNotification,Contingency)
from pbs.risk.forms import (ContingencyNotificationCreateForm,ContingencyNotificationUpdateForm,ContingencyNotificationListForm)
from dpaw_utils import views

import pbs.forms

class ContingencyNotificationCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Contingency Notification"
    pmodel = Contingency
    model = ContingencyNotification
    form_class = ContingencyNotificationCreateForm
    context_pobject_name = "contingency"
    one_to_many_field_name = "contingency"
    urlpattern = "contingency/<int:ppk>/notification/add/"
    urlname = "contingency_notification_create"
    template_name_suffix = "_create"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.prescription.id,))

    def update_context_data(self,context):
        super().update_context_data(context)
        context["prescription"] = self.pobject.prescription

class ContingencyNotificationUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change ContingencyNotification Plan"
    pmodel = Contingency
    model = ContingencyNotification
    form_class = ContingencyNotificationUpdateForm
    context_pobject_name = "contingency"
    one_to_many_field_name = "contingency"
    urlpattern = "contingency/<int:ppk>/notification/<int:pk>/"
    urlname = "contingency_notification_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.prescription.id,))

    def update_context_data(self,context):
        super().update_context_data(context)
        context["prescription"] = self.pobject.prescription


class ContingencyNotificationListView(pbs.forms.GetActionMixin,views.OneToManyListView):
    title = "Contingency Action"
    pmodel = Contingency
    model = ContingencyNotification
    listform_class = ContingencyNotificationListForm
    context_pobject_name = "contingency"
    one_to_many_field_name = "contingency"
    urlpattern = "contingency/<int:ppk>/notification/"
    urlname = "contingency_notification_list"
    template_name_suffix = "_list"
    default_order = ("name","id")

    def _get_success_url(self):
        return urls.reverse("risk:prescription_contingency_list",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:contingency_notifications_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('contingency/<int:ppk>/notification/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='contingency_notification_delete_confirm'),
            path('contingency/<int:ppk>/notifications/delete', cls.as_view(),{"action":"deleteconfirmed"},name='contingency_notifications_delete'),
        ]


    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """
    def update_context_data(self,context):
        super().update_context_data(context)
        context["prescription"] = self.pobject.prescription


    def get_deleteconfirm_context(self):
        context = super().get_deleteconfirm_context()
        context["prescription"] = self.pobject.prescription

        return context
