from .views import (PrescriptionCreateView,PrescriptionListView,PrescriptionHomeView)

app_name = "prescription"
urlpatterns = []

urlpatterns.extend(PrescriptionCreateView.urlpatterns())
urlpatterns.extend(PrescriptionListView.urlpatterns())
urlpatterns.extend(PrescriptionHomeView.urlpatterns())

