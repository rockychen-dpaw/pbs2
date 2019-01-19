from django import urls
from django.urls import path 

from pbs.stakeholder.models import (CriticalStakeholder,)
from pbs.stakeholder.forms import (CriticalStakeholderListUpdateForm,CriticalStakeholderListForm)
from dpaw_utils.views import (OneToManyListUpdateView,)
from pbs.prescription.models import (Prescription,)
import pbs.forms

class CriticalStakeholderListUpdateView(pbs.forms.GetActionMixin,OneToManyListUpdateView):
    model=CriticalStakeholder
    listform_class = CriticalStakeholderListUpdateForm
    urlpattern = "criticalstakeholder/prescription/<int:ppk>/"
    urlname = "{}_changelist"
    one_to_many_field_name = "prescription"
    pmodel = Prescription
    ppk_url_kwarg = "ppk"
    context_pobject_name = "prescription"
    title = "Critical Stakeholders"

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/criticalstakeholder/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_criticalstakeholder_delete_confirm'),
            path('prescription/<int:ppk>/criticalstakeholders/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_criticalstakeholders_delete'),
        ]

    @property
    def deleteconfirm_url(self):
        return urls.reverse("stakeholder:prescription_criticalstakeholders_delete",args=(self.pobject.id,))

    def _get_success_url(self):
        return urls.reverse("stakeholder:criticalstakeholder_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return CriticalStakeholderListForm
        else:
            return super().get_listform_class()


