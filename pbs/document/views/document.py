
from django.urls import path 
from django import urls

from django_downloadview import ObjectDownloadView

from pbs.document.models import (Document,)
from pbs.prescription.models import (Prescription,)
from pbs.document.forms import (TaggedDocumentCreateForm,DocumentListForm)
from dpaw_utils import views
import pbs.forms

class PrescriptionDocumentCreateView(views.RequestActionMixin,views.SendDataThroughGetMixin,views.OneToManyCreateView):
    pmodel = Prescription
    model = Document
    form_class = TaggedDocumentCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "document/add/prescription/<int:ppk>/"
    urlname = "prescription_document_update"
    template_name_suffix = "_create"
    default_action = "upload"

    @classmethod
    def _get_extra_urlpatterns(cls):
        return [
            path('<int:pk>/download', ObjectDownloadView.as_view(model=Document, file_field='document'),{"action":"download"},name='document_download'),
        ]

    @property
    def title(self):
        try:
            form = self.get_form()
            return "Add {} docment".format(form.instance.tag.name)
        except:
            return "Add document"

    def get_success_url(self):
        return urls.reverse("risk:context_update",args=(self.pobject.id,))

    def get_action(self,action_name):
        return pbs.forms.get_action(action_name)


class PrescriptionDocumentsView(views.OneToManyListView):
    pmodel = Prescription
    model = Document
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/document"
    urlname = "prescription_documents"
    template_name_suffix = "_list"

    listform_class = DocumentListForm

    @classmethod
    def _get_extra_urlpatterns(cls):
        return [
            path('prescription/<int:ppk>/document/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_documents_delete_confirm'),
            path('prescription/<int:ppk>/document/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_documents_delete'),
        ]

    @property
    def deleteconfirm_url(self):
        return urls.reverse("document:prescription_documents_delete",args=(self.pobject.id,))

    def get_success_url(self):
        return urls.reverse("risk:context_update",args=(self.pobject.id,))

    def get_action(self,action_name):
        return pbs.forms.get_action(action_name)
