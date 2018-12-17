from .views import (PrescriptionDocumentCreateView,PrescriptionDocumentsView)


app_name = "document"
urlpatterns = []

urlpatterns.extend(PrescriptionDocumentCreateView.urlpatterns())
urlpatterns.extend(PrescriptionDocumentsView.urlpatterns())


