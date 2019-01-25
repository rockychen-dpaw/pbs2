
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.document.models import (Document,)

from dpaw_utils import forms

class DocumentCleanMixin(object):
    pass

class DocumentConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "createdate":forms.fields.AliasFieldFactory(Document,'created'),
            "delete":forms.fields.AliasFieldFactory(Document,"id",field_class=forms.fields.IntegerField),
        }
        labels = {
            "createdate":"Document created",
            "created":"Uploaded on",
            "delete":""
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "document.edit":forms.widgets.TemplateWidgetFactory(forms.widgets.FileInput,"{{}} <span>{}</span>".format(Document._meta.get_field('document').help_text))(attrs={"style":"height:35px"}),
            "createdate.view":forms.widgets.DatetimeDisplay("%d-%m-%Y"),
            "created.view":forms.widgets.DatetimeDisplay("%d-%m-%Y %H:%M:%S"),
            "modified.view":forms.widgets.DatetimeDisplay("%d-%m-%Y %H:%M:%S"),
            "delete.view":forms.widgets.HyperlinkFactory("id","document:prescription_documents_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template='<img onclick="window.location=\'{url}\'" src="/static/img/delete.png" style="width:16px;height:16px;cursor:pointer"></img>')
        }

class DocumentFilterForm(DocumentConfigMixin,forms.FilterForm):
    all_buttons = [
        BUTTON_ACTIONS["update_selection"],
    ]

    class Meta:
        model = Document
        purpose = (('filter','edit'),"view")
        all_fields = ("tag","document_archived")

class DocumentBaseForm(DocumentCleanMixin,DocumentConfigMixin,forms.ModelForm):
    class Meta:
        pass

class TaggedDocumentCreateForm(forms.EditableFieldsMixin,DocumentBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["upload"],
    ]
    class Meta:
        model = Document
        purpose = (('tagged','edit'),"view")
        all_fields = ("tag","document",)
        editable_fields = ("tag","document",)
        ordered_fields = ("document",)

class DocumentUpdateForm(forms.EditableFieldsMixin,DocumentBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["upload"],
    ]
    class Meta:
        model = Document
        purpose = ('edit','view')
        all_fields = ("document",)
        editable_fields = ("document",)


class DocumentBaseListForm(DocumentConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class DocumentListForm(DocumentBaseListForm):
    all_actions = [
        OPTION_ACTIONS["delete_selected_documents"],
        OPTION_ACTIONS["archive_selected_documents"],
    ]
    def __init__(self, *args, **kwargs):
        super(DocumentListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Document
        all_fields = ("category","tag","createdate","created","creator","delete")
        
        editable_fields = []
        ordered_fields = ("category","tag","createdate","created","creator","delete")


class DocumentConfirmListForm(DocumentBaseListForm):
    all_actions = [
        OPTION_ACTIONS["delete_selected_documents"],
        OPTION_ACTIONS["archive_selected_documents"],
    ]
    def __init__(self, *args, **kwargs):
        super(DocumentConfirmListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Document
        all_fields = ("category","tag","document","document_archived","created","creator","modified","modifier")
        
        editable_fields = []

