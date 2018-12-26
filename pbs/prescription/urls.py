from .views import (PrescriptionCreateView,PrescriptionListView,PrescriptionHomeView,PrescriptionUpdateView,PrescriptionRegionalObjectivesUpdateView,PrescriptionObjectivesUpdateView)

app_name = "prescription"
urlpatterns = []

urlpatterns.extend(PrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionListView.urlpatterns())
urlpatterns.extend(PrescriptionHomeView.urlpatterns())
urlpatterns.extend(PrescriptionUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRegionalObjectivesUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionObjectivesUpdateView.urlpatterns())

