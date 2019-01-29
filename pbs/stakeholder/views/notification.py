from django import urls
from django.urls import path 

from pbs.stakeholder.models import (Notification,)
from pbs.stakeholder.forms import (NotificationListUpdateForm,NotificationListForm)
from dpaw_utils.views import (OneToManyListUpdateView,)
from pbs.prescription.models import (Prescription,)
import pbs.forms

class PrescriptionNotificationListUpdateView(pbs.forms.GetActionMixin,OneToManyListUpdateView):
    model=Notification
    listform_class = NotificationListUpdateForm
    urlpattern = "notification/prescription/<int:ppk>/"
    urlname = "prescription_notification_changelist"
    one_to_many_field_name = "prescription"
    pmodel = Prescription
    ppk_url_kwarg = "ppk"
    context_pobject_name = "prescription"
    title = "Notifications"

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/notification/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_notification_delete_confirm'),
            path('prescription/<int:ppk>/notifications/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_notifications_delete'),
        ]

    @property
    def deleteconfirm_url(self):
        return urls.reverse("stakeholder:prescription_notifications_delete",args=(self.pobject.id,))

    def _get_success_url(self):
        return urls.reverse("stakeholder:prescription_notification_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return NotificationListForm
        else:
            return super().get_listform_class()


