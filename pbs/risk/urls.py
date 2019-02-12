from .views import (ContextUpdateView,PrescriptionComplexitiesUpdateView,PrescriptionRegistersUpdateView,
        PrescriptionRiskCreateView,PrescriptionMultipleActionCreateView,
        PrescriptionTreatmentDetailView,
        PrescriptionActionUpdateView,PrescriptionActionsUpdateView,PrescriptionPreBurnActionsUpdateView,PrescriptionDayOfBurnActionsUpdateView,PrescriptionPostBurnActionsUpdateView,
        PrescriptionContingencyCreateView,PrescriptionContingencyUpdateView,PrescriptionContingencyListView,
        ContingencyActionCreateView,ContingencyActionUpdateView,ContingencyActionListView,
        ContingencyNotificationCreateView,ContingencyNotificationUpdateView,ContingencyNotificationListView,
        )


app_name = "risk"
urlpatterns = []

urlpatterns.extend(ContextUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionComplexitiesUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRegistersUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionRiskCreateView.urlpatterns())
urlpatterns.extend(PrescriptionTreatmentDetailView.urlpatterns())
urlpatterns.extend(PrescriptionActionUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionActionsUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionPreBurnActionsUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionDayOfBurnActionsUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionPostBurnActionsUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionMultipleActionCreateView.urlpatterns())

urlpatterns.extend(PrescriptionContingencyCreateView.urlpatterns())
urlpatterns.extend(PrescriptionContingencyUpdateView.urlpatterns())
urlpatterns.extend(PrescriptionContingencyListView.urlpatterns())

urlpatterns.extend(ContingencyActionCreateView.urlpatterns())
urlpatterns.extend(ContingencyActionUpdateView.urlpatterns())
urlpatterns.extend(ContingencyActionListView.urlpatterns())

urlpatterns.extend(ContingencyNotificationCreateView.urlpatterns())
urlpatterns.extend(ContingencyNotificationUpdateView.urlpatterns())
urlpatterns.extend(ContingencyNotificationListView.urlpatterns())

