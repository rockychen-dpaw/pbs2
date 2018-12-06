
from pbs.forms import (FORM_ACTIONS,LIST_ACTIONS)
from ..models import (Context,)
from dpaw_utils import forms

class ContextCleanMixin(object):
    pass


class ContextConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "statement.edit":forms.widgets.Textarea(attrs={"class":"vTextField"}),
        }

class ContextBaseForm(ContextCleanMixin,ContextConfigMixin,forms.ModelForm):
    class Meta:
        pass

class ContextUpdateForm(ContextBaseForm):
    all_actions = [
        FORM_ACTIONS["save"],
    ]
    class Meta:
        model = Context
        fields = ("statement",)
        editable_fields = ("statement",)
