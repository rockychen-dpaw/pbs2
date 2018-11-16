from .views import (PrescriptionCreateView,PrescriptionListView,PrescriptionUpdateView)

app_name = "prescription"
urlpatterns = []

urlpatterns.extend(PrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionListView.urlpatterns())
urlpatterns.extend(PrescriptionUpdateView.urlpatterns())

