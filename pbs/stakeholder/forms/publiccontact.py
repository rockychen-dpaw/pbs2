from dpaw_utils import forms
from django.forms.formsets import DELETION_FIELD_NAME

from pbs.stakeholder.models import (PublicContact,)
import pbs.widgets
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)

class PublicContactCleanMixin(object):
    pass


class PublicContactConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(PublicContact,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(PublicContact,"id",field_class=forms.fields.IntegerField)
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            'organisation.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'person.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'comments.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "id.edit":forms.widgets.Hidden(),
            "delete.view":forms.widgets.HyperlinkFactory("id","stakeholder:prescription_publiccontact_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }
        labels = {
            "delete":""
        }


class PublicContactMemberUpdateForm(PublicContactCleanMixin,PublicContactConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") \
           and not self.cleaned_data.get("organisation") \
           and not self.cleaned_data.get("person") \
           and not self.cleaned_data.get("comments") \
           and not self.cleaned_data.get("name") 

    class Meta:
        model = PublicContact
        field_required_flag = False
        all_fields = ("id","name","organisation","person","comments","delete")
        editable_fields = ("id","name","organisation","person","comments")


PublicContactListUpdateForm = forms.listupdateform_factory(PublicContactMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True)
        
class PublicContactBaseListForm(PublicContactConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))


class PublicContactListForm(PublicContactBaseListForm):
    class Meta:
        model = PublicContact
        all_fields = ("id","name","organisation","person","comments")
