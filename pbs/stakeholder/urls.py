from .views import (CriticalStakeholderListUpdateView,PrescriptionNotificationListUpdateView,)


app_name = "stakeholder"
urlpatterns = []

urlpatterns.extend(CriticalStakeholderListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionNotificationListUpdateView.urlpatterns())


