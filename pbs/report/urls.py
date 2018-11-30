from .views import (SummaryCompletionStateUpdateView,BurnImplementationStateUpdateView,BurnClosureStateUpdateView)

app_name = "report"
urlpatterns = []

urlpatterns.extend(SummaryCompletionStateUpdateView.urlpatterns())
urlpatterns.extend(BurnImplementationStateUpdateView.urlpatterns())
urlpatterns.extend(BurnClosureStateUpdateView.urlpatterns())

for p in urlpatterns:
    print(p)

