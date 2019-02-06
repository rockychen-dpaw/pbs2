from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (RoadSegment,)

from dpaw_utils import forms

class RoadSegmentCleanMixin(object):
    pass

class RoadSegmentConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "delete":forms.fields.AliasFieldFactory(RoadSegment,"id",field_class=forms.fields.IntegerField),
            "id":forms.fields.OverrideFieldFactory(RoadSegment,"id",forms.fields.IntegerField,field_params={"required":False}),
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
            'road_type.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'traffic_considerations.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","implementation:prescription_roadsegment_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class RoadSegmentBaseForm(RoadSegmentCleanMixin,RoadSegmentConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class RoadSegmentUpdateForm(RoadSegmentBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
    ]
    class Meta:
        model = RoadSegment
        all_fields = ("name",)


class RoadSegmentMemberUpdateForm(RoadSegmentCleanMixin,RoadSegmentConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") \
           and not self.cleaned_data.get("name")  \
           and not self.cleaned_data.get("road_type") \
           and not self.cleaned_data.get("traffic_considerations") \
           and not self.cleaned_data.get("signs_installed") \
           and not self.cleaned_data.get("signs_removed") \
           and not self.cleaned_data.get("traffic_diagram")

    class Meta:
        model = RoadSegment
        widths = {
            "delete":"16px"
        }
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("id","name","road_type","traffic_considerations","traffic_diagram","signs_installed","signs_removed","delete")
        editable_fields = ("id","name","road_type","traffic_considerations","traffic_diagram","signs_installed","signs_removed")

RoadSegmentListUpdateForm = forms.listupdateform_factory(RoadSegmentMemberUpdateForm,min_num=0,max_num=400,extra=1,primary_field="id",all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=True)

class RoadSegmentBaseListForm(RoadSegmentConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class RoadSegmentListForm(RoadSegmentBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(RoadSegmentListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RoadSegment
        all_fields = ("name","road_type","traffic_considerations","traffic_diagram","signs_installed","signs_removed")
        editable_fields = []

