from .views import (PrescriptionOperationalOverviewUpdateView,PrescriptionRoadSegmentListUpdateView,
        PrescriptionTrailSegmentListUpdateView,
        PrescriptionBurningPrescriptionCreateView,PrescriptionBurningPrescriptionUpdateView,PrescriptionBurningPrescriptionListView)


app_name = "implementation"
urlpatterns = []

urlpatterns.extend(PrescriptionOperationalOverviewUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRoadSegmentListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionTrailSegmentListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionBurningPrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionBurningPrescriptionUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionBurningPrescriptionListView.urlpatterns())


