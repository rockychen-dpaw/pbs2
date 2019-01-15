from .views import (PrescriptionOperationalOverviewUpdateView,)


app_name = "implementation"
urlpatterns = []

urlpatterns.extend(PrescriptionOperationalOverviewUpdateView.urlpatterns())


