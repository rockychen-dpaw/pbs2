from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (EdgingPlan,)

from dpaw_utils import forms

class EdgingPlanCleanMixin(object):
    def clean_ros_max(self):
        max_value = self.cleaned_data.get("ros_max")
        min_value = self.cleaned_data.get("ros_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min ROS")
        return max_value

    def clean_ffdi_max(self):
        max_value = self.cleaned_data.get("ffdi_max")
        min_value = self.cleaned_data.get("ffdi_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min FFDI")
        return max_value

    def clean_grassland_curing_max(self):
        max_value = self.cleaned_data.get("grassland_curing_max")
        min_value = self.cleaned_data.get("grassland_curing_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min grassland curing")
        return max_value

    def clean_gfdi_max(self):
        max_value = self.cleaned_data.get("gfdi_max")
        min_value = self.cleaned_data.get("gfdi_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min GFDI")
        return max_value

    def clean_wind_max(self):
        max_value = self.cleaned_data.get("wind_max")
        min_value = self.cleaned_data.get("wind_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min wind speed")
        return max_value

class EdgingPlanConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "ros_min":forms.fields.MultipleFieldFactory(EdgingPlan,"ros_min",('ros_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "ffdi_min":forms.fields.MultipleFieldFactory(EdgingPlan,"ffdi_min",('ffdi_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "grassland_curing_min":forms.fields.MultipleFieldFactory(EdgingPlan,"grassland_curing_min",('grassland_curing_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "gfdi_min":forms.fields.MultipleFieldFactory(EdgingPlan,"gfdi_min",('gfdi_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "wind_min":forms.fields.MultipleFieldFactory(EdgingPlan,"wind_min",('wind_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "delete":forms.fields.AliasFieldFactory(EdgingPlan,"id",field_class=forms.fields.IntegerField),
        }
        labels = {
            "delete":"",
            "ros_min":"ROS Range",
            "ffdi_min":"FFDI Range",
            "grassland_curing_min":"GLC Range",
            "gfdi_min":"GFDI Range",
            "wind_min":"Wind Speed Range(km/h)",
            "rh_min":"RH Range(%)"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "location.list":forms.widgets.HyperlinkFactory("location","implementation:prescription_edgingplan_update",ids=[("id","pk"),("prescription","ppk")]),
            'sdi.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'wind_dir.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","implementation:prescription_edgingplan_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<img title='Delete' onclick='window.location=\"{url}\"' src='/static/img/delete.png' style='width:16px;height:16px;cursor:pointer'>")
        }

class EdgingPlanBaseForm(EdgingPlanCleanMixin,EdgingPlanConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class EdgingPlanCreateForm(EdgingPlanBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = EdgingPlan
        purpose = ("edit","view")
        all_fields = ("location","fuel_type","desirable_reason","strategies","ffdi_min","ffdi_max","gfdi_min","gfdi_max","ros_min","ros_max","sdi",
                "grassland_curing_min","grassland_curing_max","wind_min","wind_max","wind_dir")
        editable_fields = ("location","fuel_type","desirable_reason","strategies","ffdi_min","ffdi_max","gfdi_min","gfdi_max","ros_min","ros_max","sdi",
                "grassland_curing_min","grassland_curing_max","wind_min","wind_max","wind_dir")
        ordered_fields = ("location","fuel_type","desirable_reason","strategies","ffdi_min","gfdi_min","ros_min","sdi","grassland_curing_min","wind_min","wind_dir")

class EdgingPlanUpdateForm(EdgingPlanCreateForm):
    pass

class EdgingPlanBaseListForm(EdgingPlanConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class EdgingPlanListForm(EdgingPlanBaseListForm):
    def __init__(self, *args, **kwargs):
        super(EdgingPlanListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = EdgingPlan
        widths = {
            "delete":"16px"
        }
        all_fields = ("location","fuel_type","desirable_reason","strategies","ffdi_min","ffdi_max","gfdi_min","gfdi_max","ros_min","ros_max","sdi",
                "grassland_curing_min","grassland_curing_max","wind_min","wind_max","wind_dir","delete")
        editable_fields = []
        ordered_fields = ("location","fuel_type","desirable_reason","strategies","ffdi_min","gfdi_min","ros_min","sdi","grassland_curing_min","wind_min","wind_dir","delete")

