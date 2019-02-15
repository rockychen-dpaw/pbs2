
from django.urls import path 
from django import urls
from django.db import transaction
from django.http import (HttpResponseRedirect,)
from django.contrib import messages

from django_downloadview import ObjectDownloadView

from pbs.document.models import (Document,DocumentTag,documentcategory_list)
from pbs.document.filters import (DocumentFilter,)
from pbs.prescription.models import (Prescription,)
from pbs.document.forms import (TaggedDocumentCreateForm,DocumentCreateForm,DocumentListForm,DocumentConfirmListForm,DocumentFilterForm)
import pbs.forms
from dpaw_utils import views
from dpaw_utils.forms.utils import ChainDict
from dpaw_utils.forms import filters

class PrescriptionDocumentCreateView(pbs.forms.GetActionMixin,views.RequestActionMixin,views.SendDataThroughUrlMixin,views.OneToManyCreateView):
    pmodel = Prescription
    model = Document
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/document/add"
    urlname = "prescription_document_add"
    template_name_suffix = "_add"
    default_post_action = "upload"

    data_in_url = True

    @classmethod
    def _get_extra_urlpatterns(cls):
        return [
            path('<int:pk>/download', ObjectDownloadView.as_view(model=Document, file_field='document'),{"action":"download"},name='document_download'),
            path('prescription/<int:ppk>/document/tag/<int:tag>/add', cls.as_view(),name='prescription_taggeddocument_add'),
        ]

    @property
    def title(self):
        try:
            form = self.get_form()
            return "Add {} docment".format(form.instance.tag.name)
        except:
            return "Add document"

    def get_form_class(self):
        if "tag" in self.kwargs:
            return TaggedDocumentCreateForm
        else:
            return DocumentCreateForm

    def _get_success_url(self):
        return urls.reverse("document:prescription_document_list",args=(self.pobject.id,))

class PrescriptionDocumentsView(pbs.forms.GetActionMixin,views.OneToManyListView):
    pmodel = Prescription
    model = Document
    filter_class = DocumentFilter
    filterform_class = DocumentFilterForm
    listform_class = DocumentListForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/document/"
    urlname = "prescription_document_list"
    filtertool = False

    @classmethod
    def _get_extra_urlpatterns(cls):
        return [
            path('prescription/<int:ppk>/document/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_documents_delete_confirm'),
            path('prescription/<int:ppk>/document/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_documents_delete'),
            path('prescription/<int:ppk>/document/<int:pk>/archiveconfirm', cls.as_view(),{"action":"archiveconfirm"},name='prescription_documents_archive_confirm'),
            path('prescription/<int:ppk>/document/archive', cls.as_view(),{"action":"archiveconfirmed"},name='prescription_documents_archive'),
            path('prescription/<int:ppk>/document/tag/<int:tag>/', cls.as_view(),name='prescription_taggeddocument_list'),
        ]


    @property
    def template_name_suffix(self):
        if "tag" in self.kwargs:
            return "_tagged_list"
        else:
            return "_list"

    @property
    def title(self):
        try:
            return "{} List".format(DocumentTag.objects.get(id = self.kwargs["tag"]).name)
        except:
            return "Document List"


    @property
    def deleteconfirm_url(self):
        return urls.reverse("document:prescription_documents_delete",args=(self.pobject.id,))

    @property
    def archiveconfirm_url(self):
        return urls.reverse("document:prescription_documents_archive",args=(self.pobject.id,))

    def get_filterform_data(self):
        try:
            return ChainDict([{"tag":self.kwargs["tag"]},self.request.GET,{"document_archived":False}])
        except:
            return self.request.GET

    def _get_success_url(self):
        return urls.reverse("document:prescription_document_list",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action:
            return DocumentConfirmListForm
        else:
            return DocumentListForm

    def update_context_data(self,context):
        super().update_context_data(context)
        try:
            context["tag"] = DocumentTag.objects.get(id = self.kwargs["tag"])
        except:
            context["archivestatuslist"] = ((True,"Yes"),(False,"No"))
            context["categorylist"] = documentcategory_list
            context["modifiedlist"] = filters.DateRangeFilter.choices
            userlist = set()
            for o in self.object_list:
                if o.modifier:
                    userlist.add(o.modifier)
            context["modifierlist"] = sorted(userlist,key=lambda u:u.username)

    def archiveconfirmed_post(self):
        document_list = self.get_queryset_4_selected()
        for doc in document_list:
            try:
                doc.document_archived = True
                doc.save(update_fields=["document_archived","modifier","modified"])
            except Exception as ex:
                messages.add_message(self.request,messages.ERROR,"Failed to archive document {} dut to {}".format(doc, ex))

        return HttpResponseRedirect(self.get_success_url())



