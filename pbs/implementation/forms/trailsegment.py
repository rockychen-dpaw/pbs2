from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (TrailSegment,)

from dpaw_utils import forms

class TrailSegmentCleanMixin(object):
    pass

class TrailSegmentConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "delete":forms.fields.AliasFieldFactory(TrailSegment,"id",field_class=forms.fields.IntegerField),
            "id":forms.fields.OverrideFieldFactory(TrailSegment,"id",forms.fields.IntegerField,field_params={"required":False}),
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            'signs_installed.edit':forms.widgets.DateInput(maxdate=False,attrs={"style":"width:80px"}),
            'signs_removed.edit':forms.widgets.DateInput(maxdate=False,attrs={"style":"width:80px"}),
            'start.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'start_signage.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'stop.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'stop_signage.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","implementation:prescription_trailsegment_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class TrailSegmentBaseForm(TrailSegmentCleanMixin,TrailSegmentConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class TrailSegmentUpdateForm(TrailSegmentBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
    ]
    class Meta:
        model = TrailSegment
        all_fields = ("name",)


class TrailSegmentMemberUpdateForm(TrailSegmentCleanMixin,TrailSegmentConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") \
           and not self.cleaned_data.get("name")  \
           and not self.cleaned_data.get("signs_installed") \
           and not self.cleaned_data.get("signs_removed") \
           and not self.cleaned_data.get("diversion") \
           and not self.cleaned_data.get("start") \
           and not self.cleaned_data.get("start_signage") \
           and not self.cleaned_data.get("stop") \
           and not self.cleaned_data.get("stop_signage") 

    class Meta:
        model = TrailSegment
        widths = {
            "delete":"16px"
        }
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("id","name","diversion","start","start_signage","stop","stop_signage","signs_installed","signs_removed","delete")
        editable_fields = ("id","name","diversion","start","start_signage","stop","stop_signage","signs_installed","signs_removed")

TrailSegmentListUpdateForm = forms.listupdateform_factory(TrailSegmentMemberUpdateForm,min_num=0,max_num=400,extra=1,primary_field="id",all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=True)

class TrailSegmentBaseListForm(TrailSegmentConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class TrailSegmentListForm(TrailSegmentBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(TrailSegmentListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = TrailSegment
        all_fields = ("name","diversion","start","start_signage","stop","stop_signage","signs_installed","signs_removed","delete")
        editable_fields = []

