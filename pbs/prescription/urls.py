from .views import (PrescriptionCreateView,PrescriptionListView,PrescriptionHomeView,PrescriptionUpdateView)

app_name = "prescription"
urlpatterns = []

urlpatterns.extend(PrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionListView.urlpatterns())
urlpatterns.extend(PrescriptionHomeView.urlpatterns())
urlpatterns.extend(PrescriptionUpdateView.urlpatterns())

