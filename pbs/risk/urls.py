from .views import (ContextUpdateView,PrescriptionComplexitiesUpdateView,PrescriptionRegistersUpdateView,
        PrescriptionRiskCreateView,
        PrescriptionActionUpdateView,PrescriptionActionsUpdateView,PrescriptionPreBurnActionsUpdateView,PrescriptionMultipleActionCreateView)


app_name = "risk"
urlpatterns = []

urlpatterns.extend(ContextUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionComplexitiesUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRegistersUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRiskCreateView.urlpatterns())
urlpatterns.extend(PrescriptionActionUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionActionsUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionPreBurnActionsUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionMultipleActionCreateView.urlpatterns())


