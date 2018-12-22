from .views import (CriticalStakeholderListUpdateView,)


app_name = "stakeholder"
urlpatterns = []

urlpatterns.extend(CriticalStakeholderListUpdateView.urlpatterns())


