from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.prescription.forms import (PrescriptionMaximumDraftRiskForm,)
from pbs.risk.models import (Action,Risk)
from pbs.risk.forms import (ActionListUpdateForm,ActionListForm,ActionFilterForm)
from pbs.risk.filters import (ActionFilter,)
from dpaw_utils import views
import pbs.forms

class PrescriptionActionsUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Plan Actions"
    pmodel = Prescription
    model = Action
    filter_class = ActionFilter
    filterform_class = ActionFilterForm
    listform_class = ActionListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/"
    urlname = "prescription_action_changelist"
    filtertool = False


    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:prescription_actions_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/action/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_action_delete_confirm'),
            path('prescription/<int:ppk>/actions/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_actions_delete'),
        ]

    def get_success_url(self):
        return urls.reverse("risk:prescription_action_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return ActionListForm
        else:
            return super().get_listform_class()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        return context
