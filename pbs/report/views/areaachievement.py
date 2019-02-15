from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.prescription.forms import (ClosePrescriptionForm,)
from pbs.report.models import (AreaAchievement,)
from pbs.report.forms import (AreaAchievementListUpdateForm,AreaAchievementListForm,)
from dpaw_utils import views

import pbs.forms

class PrescriptionAreaAchievementListUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Roads Associated With the Burn Plan"
    pmodel = Prescription
    model = AreaAchievement
    pform_class = ClosePrescriptionForm
    context_pobject_name = "prescription"
    context_pform_name = "prescriptionform"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/areaachievement/"
    urlname = "prescription_areaachievement_changelist"
    template_name_suffix = "_changelist"
    default_order = ("ignition","id")
    atomic_update = False
    errorform_keys = ("listform","prescriptionform")

    def get_mediaforms(self):
        return (self.get_listform_class(),ClosePrescriptionForm)

    def _get_success_url(self):
        return urls.reverse("report:prescription_areaachievement_changelist",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("report:prescription_areaachievements_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/areaachievement/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_areaachievement_delete_confirm'),
            path('prescription/<int:ppk>/areaachievements/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_areaachievements_delete'),
        ]

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return AreaAchievementListForm
        elif self.pobject.ignition_status == Prescription.IGNITION_COMPLETE:
            return AreaAchievementListForm
        else:
            return AreaAchievementListUpdateForm

    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

