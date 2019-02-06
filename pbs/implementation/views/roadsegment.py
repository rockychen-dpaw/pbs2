from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.implementation.models import (RoadSegment,TrafficControlDiagram)
from pbs.implementation.forms import (RoadSegmentListUpdateForm,RoadSegmentListForm,TrafficControlDiagramListForm)
from dpaw_utils import views

import pbs.forms

class PrescriptionRoadSegmentListUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Roads Associated With the Burn Plan"
    pmodel = Prescription
    model = RoadSegment
    listform_class = RoadSegmentListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/roadsegment/"
    urlname = "prescription_roadsegment_changelist"
    template_name_suffix = "_changelist"
    default_order = ("name",)

    def _get_success_url(self):
        return urls.reverse("implementation:prescription_roadsegment_changelist",args=(self.pobject.id,))

    @property
    def deleteconfirm_url(self):
        return urls.reverse("implementation:prescription_roadsegments_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/roadsegment/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_roadsegment_delete_confirm'),
            path('prescription/<int:ppk>/roadsegments/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_roadsegments_delete'),
        ]

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return RoadSegmentListForm
        else:
            return super().get_listform_class()

    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["trafficdiagramlistform"] = TrafficControlDiagramListForm(instance_list=[o.traffic_diagram for o in self.object_list if o.traffic_diagram])
        context["documents"] = self.pobject.document_set.filter(tag__id=199)

        return context

