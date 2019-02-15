from .views import (SummaryCompletionStateUpdateView,BurnImplementationStateUpdateView,BurnClosureStateUpdateView,
        PrescriptionAreaAchievementListUpdateView,
        )

app_name = "report"
urlpatterns = []

urlpatterns.extend(SummaryCompletionStateUpdateView.urlpatterns())
urlpatterns.extend(BurnImplementationStateUpdateView.urlpatterns())
urlpatterns.extend(BurnClosureStateUpdateView.urlpatterns())

urlpatterns.extend(PrescriptionAreaAchievementListUpdateView.urlpatterns())

