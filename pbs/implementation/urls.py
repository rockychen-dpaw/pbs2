from .views import (PrescriptionOperationalOverviewUpdateView,PrescriptionRoadSegmentListUpdateView,PrescriptionTrailSegmentListUpdateView)


app_name = "implementation"
urlpatterns = []

urlpatterns.extend(PrescriptionOperationalOverviewUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRoadSegmentListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionTrailSegmentListUpdateView.urlpatterns())


