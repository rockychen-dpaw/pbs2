
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from ..models import (Document,)

from dpaw_utils import forms

class DocumentCleanMixin(object):
    pass

class DocumentConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "tag.tagged":forms.widgets.Hidden(),
            "document.edit":forms.widgets.TemplateWidgetFactory(forms.widgets.FileInput,"{{}} <span>{}</span>".format(Document._meta.get_field('document').help_text)),
            "modified":forms.widgets.DatetimeDisplay("%d-%m-%Y %H:%M:%S"),
        }

class DocumentBaseForm(DocumentCleanMixin,DocumentConfigMixin,forms.ModelForm):
    class Meta:
        pass

class TaggedDocumentCreateForm(forms.EditableFieldsMixin,DocumentBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["upload_document"],
    ]
    class Meta:
        model = Document
        purpose = ('tagged','edit')
        all_fields = ("tag","document")
        editable_fields = ("tag","document")

class DocumentUpdateForm(forms.EditableFieldsMixin,DocumentBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["upload_document"],
    ]
    class Meta:
        model = Document
        purpose = ('edit',)
        all_fields = ("document",)
        editable_fields = ("document",)


class DocumentBaseListForm(DocumentConfigMixin,forms.ListForm):
    class Meta:
        purpose = ('list','view')

class DocumentListForm(DocumentBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(DocumentListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Document
        all_fields = ("prescription","category","tag","document","modified","modifier")
        
        editable_fields = []
        ordered_fields = ("prescription","category","tag","document","modified","modifier")


