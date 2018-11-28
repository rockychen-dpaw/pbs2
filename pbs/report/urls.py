from .views import (SummaryCompletionStateUpdateView,BurnImplementationStateUpdateView)

app_name = "report"
urlpatterns = []

urlpatterns.extend(SummaryCompletionStateUpdateView.urlpatterns())
urlpatterns.extend(BurnImplementationStateUpdateView.urlpatterns())

for p in urlpatterns:
    print(p)

