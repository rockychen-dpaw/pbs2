from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (TrafficControlDiagram,)

from dpaw_utils import forms

class TrafficControlDiagramCleanMixin(object):
    pass

class TrafficControlDiagramConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "size":forms.fields.CharField,
        }
        labels = {
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            'road_type.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'name.view':forms.widgets.HyperlinkFactory("name",lambda instance:instance.path.url if instance.path else None,template="""
            <a href="{url}"> <i class="icon-file"></i> {widget}</a>
            """)
        }

class TrafficControlDiagramBaseForm(TrafficControlDiagramCleanMixin,TrafficControlDiagramConfigMixin,forms.ModelForm):
    class Meta:
        pass

class TrafficControlDiagramBaseListForm(TrafficControlDiagramConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class TrafficControlDiagramListForm(TrafficControlDiagramBaseListForm):
    def __init__(self, *args, **kwargs):
        super(TrafficControlDiagramListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = TrafficControlDiagram
        all_fields = ("name","path","size")
        editable_fields = []

