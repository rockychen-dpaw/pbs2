from .views import (PrescriptionCreateView,PrescriptionListView)

app_name = "prescription"
urlpatterns = []

urlpatterns.extend(PrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionListView.urlpatterns())

