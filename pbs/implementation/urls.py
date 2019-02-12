from .views import (PrescriptionOperationalOverviewUpdateView,
        PrescriptionRoadSegmentListUpdateView,
        PrescriptionTrailSegmentListUpdateView,
        PrescriptionBurningPrescriptionCreateView,PrescriptionBurningPrescriptionUpdateView,PrescriptionBurningPrescriptionListView,
        PrescriptionEdgingPlanCreateView,PrescriptionEdgingPlanUpdateView,PrescriptionEdgingPlanListView,
        PrescriptionExclusionAreaListUpdateView,
        PrescriptionLightingSequenceCreateView,PrescriptionLightingSequenceUpdateView,PrescriptionLightingSequenceListView,
        )


app_name = "implementation"
urlpatterns = []

urlpatterns.extend(PrescriptionOperationalOverviewUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRoadSegmentListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionTrailSegmentListUpdateView.urlpatterns())

urlpatterns.extend(PrescriptionBurningPrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionBurningPrescriptionUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionBurningPrescriptionListView.urlpatterns())

urlpatterns.extend(PrescriptionEdgingPlanCreateView.urlpatterns())
urlpatterns.extend(PrescriptionEdgingPlanUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionEdgingPlanListView.urlpatterns())

urlpatterns.extend(PrescriptionExclusionAreaListUpdateView.urlpatterns())

urlpatterns.extend(PrescriptionLightingSequenceCreateView.urlpatterns())
urlpatterns.extend(PrescriptionLightingSequenceUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionLightingSequenceListView.urlpatterns())

