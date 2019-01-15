from .views import (ContextUpdateView,PrescriptionComplexitiesUpdateView,PrescriptionRegistersUpdateView,
        PrescriptionActionUpdateView,PrescriptionActionsUpdateView)


app_name = "risk"
urlpatterns = []

urlpatterns.extend(ContextUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionComplexitiesUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRegistersUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionActionUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionActionsUpdateView.urlpatterns())


