from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (BurningPrescription,)

from dpaw_utils import forms

class BurningPrescriptionCleanMixin(object):
    def clean_max_area(self):
        max_value = self.cleaned_data.get("max_area")
        min_value = self.cleaned_data.get("min_area")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min area")
        return max_value

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

    def clean_temp_max(self):
        max_value = self.cleaned_data.get("temp_max")
        min_value = self.cleaned_data.get("temp_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min temperature")
        return max_value

    def clean_rh_max(self):
        max_value = self.cleaned_data.get("rh_max")
        min_value = self.cleaned_data.get("rh_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min RH")
        return max_value

    def clean_smc_max(self):
        max_value = self.cleaned_data.get("smc_max")
        min_value = self.cleaned_data.get("smc_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min SMC")
        return max_value

    def clean_pmc_max(self):
        max_value = self.cleaned_data.get("pmc_max")
        min_value = self.cleaned_data.get("pmc_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min PMC")
        return max_value

    def clean_wind_max(self):
        max_value = self.cleaned_data.get("wind_max")
        min_value = self.cleaned_data.get("wind_min")
        if min_value is not None and max_value is not None:
            if min_value > max_value:
                raise forms.ValidationError("Must greater than or equal to min wind speed")
        return max_value

class BurningPrescriptionConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "min_area":forms.fields.MultipleFieldFactory(BurningPrescription,"min_area",('max_area',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "ros_min":forms.fields.MultipleFieldFactory(BurningPrescription,"ros_min",('ros_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "ffdi_min":forms.fields.MultipleFieldFactory(BurningPrescription,"ffdi_min",('ffdi_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "grassland_curing_min":forms.fields.MultipleFieldFactory(BurningPrescription,"grassland_curing_min",('grassland_curing_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "gfdi_min":forms.fields.MultipleFieldFactory(BurningPrescription,"gfdi_min",('gfdi_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "temp_min":forms.fields.MultipleFieldFactory(BurningPrescription,"temp_min",('temp_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "rh_min":forms.fields.MultipleFieldFactory(BurningPrescription,"rh_min",('rh_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "smc_min":forms.fields.MultipleFieldFactory(BurningPrescription,"smc_min",('smc_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "pmc_min":forms.fields.MultipleFieldFactory(BurningPrescription,"pmc_min",('pmc_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "wind_min":forms.fields.MultipleFieldFactory(BurningPrescription,"wind_min",('wind_max',),layout = "<span style='white-space:nowrap'>{0} - {1}</span>"),
            "delete":forms.fields.AliasFieldFactory(BurningPrescription,"id",field_class=forms.fields.IntegerField),
        }
        labels = {
            "delete":"",
            "min_area":"Area to be Burnt(%)",
            "ros_min":"ROS Range",
            "ffdi_min":"FFDI Range",
            "grassland_curing_min":"GLC Range",
            "gfdi_min":"GFDI Range",
            "temp_min":"Temperature Range",
            "smc_min":"SMC Range",
            "pmc_min":"PMC Range",
            "wind_min":"Wind Speed Range(km/h)",
            "rh_min":"RH Range(%)"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "fuel_type.list":forms.widgets.HyperlinkFactory("fuel_type","implementation:prescription_burningprescription_update",ids=[("id","pk"),("prescription","ppk")]),
            'sdi.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'wind_dir.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","implementation:prescription_burningprescription_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<img title='Delete' onclick='window.location=\"{url}\"' src='/static/img/delete.png' style='width:16px;height:16px;cursor:pointer'>")
        }

class BurningPrescriptionBaseForm(BurningPrescriptionCleanMixin,BurningPrescriptionConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class BurningPrescriptionCreateForm(BurningPrescriptionBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = BurningPrescription
        purpose = ("edit","view")
        all_fields = ("fuel_type","scorch","min_area","max_area","ros_min","ros_max","ffdi_min","ffdi_max","grassland_curing_min","grassland_curing_max","gfdi_min","gfdi_max",
                "temp_min","temp_max","rh_min","rh_max","sdi","smc_min","smc_max","pmc_min","pmc_max","wind_min","wind_max","wind_dir")
        editable_fields = ("fuel_type","scorch","min_area","max_area","ros_min","ros_max","ffdi_min","ffdi_max","grassland_curing_min","grassland_curing_max","gfdi_min","gfdi_max",
                "temp_min","temp_max","rh_min","rh_max","sdi","smc_min","smc_max","pmc_min","pmc_max","wind_min","wind_max","wind_dir")
        ordered_fields = ("fuel_type","scorch","min_area","ros_min","ffdi_min","grassland_curing_min","gfdi_min","temp_min","rh_min","sdi","smc_min","pmc_min","wind_min","wind_dir")

class BurningPrescriptionUpdateForm(BurningPrescriptionCreateForm):
    pass
    class Meta:
        model = BurningPrescription
        purpose = ("edit","view")
        all_fields = ("fuel_type","scorch","min_area","max_area","ros_min","ros_max","ffdi_min","ffdi_max","grassland_curing_min","grassland_curing_max","gfdi_min","gfdi_max",
                "temp_min","temp_max","rh_min","rh_max","sdi","smc_min","smc_max","pmc_min","pmc_max","wind_min","wind_max","wind_dir")
        editable_fields = ("fuel_type","scorch","min_area","max_area","ros_min","ros_max","ffdi_min","ffdi_max","grassland_curing_min","grassland_curing_max","gfdi_min","gfdi_max",
                "temp_min","temp_max","rh_min","rh_max","sdi","smc_min","smc_max","pmc_min","pmc_max","wind_min","wind_max","wind_dir")
        ordered_fields = ("fuel_type","scorch","min_area","ros_min","ffdi_min","grassland_curing_min","gfdi_min","temp_min","rh_min","sdi","smc_min","pmc_min","wind_min","wind_dir")


class BurningPrescriptionBaseListForm(BurningPrescriptionConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class BurningPrescriptionListForm(BurningPrescriptionBaseListForm):
    def __init__(self, *args, **kwargs):
        super(BurningPrescriptionListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = BurningPrescription
        widths = {
            "delete":"16px"
        }
        all_fields = ("fuel_type","scorch","min_area","max_area","ros_min","ros_max","ffdi_min","ffdi_max","grassland_curing_min","grassland_curing_max","gfdi_min","gfdi_max",
                "temp_min","temp_max","rh_min","rh_max","sdi","smc_min","smc_max","pmc_min","pmc_max","wind_min","wind_max","wind_dir","delete")
        editable_fields = []
        ordered_fields = ("fuel_type","scorch","min_area","ros_min","ffdi_min","grassland_curing_min","gfdi_min","temp_min","rh_min","sdi","smc_min","pmc_min","wind_min","wind_dir","delete")

