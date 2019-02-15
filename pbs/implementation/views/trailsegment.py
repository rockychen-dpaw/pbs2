from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.implementation.models import (TrailSegment,)
from pbs.implementation.forms import (TrailSegmentListUpdateForm,TrailSegmentListForm)
from dpaw_utils import views

import pbs.forms

class PrescriptionTrailSegmentListUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Tracks and Trails Associated With the Burn Plan"
    pmodel = Prescription
    model = TrailSegment
    listform_class = TrailSegmentListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/trailsegment/"
    urlname = "prescription_trailsegment_changelist"
    template_name_suffix = "_changelist"
    default_order = ("name",)

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_trailsegment_changelist",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("implementation:prescription_trailsegments_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/trailsegment/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_trailsegment_delete_confirm'),
            path('prescription/<int:ppk>/trailsegments/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_trailsegments_delete'),
        ]

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return TrailSegmentListForm
        else:
            return super().get_listform_class()

    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

    def update_context_data(self,context):
        super().update_context_data(context)
        context["documents"] = self.pobject.document_set.filter(tag__id=151)

