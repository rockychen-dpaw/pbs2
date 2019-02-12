from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.implementation.models import (ExclusionArea,)

from dpaw_utils import forms

class ExclusionAreaCleanMixin(object):
    pass

class ExclusionAreaConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "delete":forms.fields.AliasFieldFactory(ExclusionArea,"id",field_class=forms.fields.IntegerField),
            "id":forms.fields.OverrideFieldFactory(ExclusionArea,"id",forms.fields.IntegerField,field_params={"required":False}),
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            'description.view':forms.widgets.TextareaDisplay(),
            'location.view':forms.widgets.TextareaDisplay(),
            'detail.view':forms.widgets.TextareaDisplay(),
            'description.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'location.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'detail.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","implementation:prescription_exclusionarea_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class ExclusionAreaBaseForm(ExclusionAreaCleanMixin,ExclusionAreaConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class ExclusionAreaUpdateForm(ExclusionAreaBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
    ]
    class Meta:
        model = ExclusionArea
        all_fields = ("description","location","detail")


class ExclusionAreaMemberUpdateForm(ExclusionAreaCleanMixin,ExclusionAreaConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") \
           and not self.cleaned_data.get("description")  \
           and not self.cleaned_data.get("location") \
           and not self.cleaned_data.get("detail") 

    class Meta:
        model = ExclusionArea
        widths = {
            "delete":"16px"
        }
        purpose = (("listedit","edit"),("list","view"))
        all_fields = ("id","location","description","detail","delete")
        editable_fields = ("id","location","description","detail")

ExclusionAreaListUpdateForm = forms.listupdateform_factory(ExclusionAreaMemberUpdateForm,min_num=0,max_num=400,extra=1,primary_field="id",all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True,can_add=True)

class ExclusionAreaBaseListForm(ExclusionAreaConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ExclusionAreaListForm(ExclusionAreaBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(ExclusionAreaListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ExclusionArea
        all_fields = ("location","description","detail","delete")
        editable_fields = []

