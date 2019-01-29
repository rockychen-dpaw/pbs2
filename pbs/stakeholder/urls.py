from .views import (CriticalStakeholderListUpdateView,PrescriptionNotificationListUpdateView,PrescriptionPublicContactListUpdateView)


app_name = "stakeholder"
urlpatterns = []

urlpatterns.extend(CriticalStakeholderListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionNotificationListUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionPublicContactListUpdateView.urlpatterns())


