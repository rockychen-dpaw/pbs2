from dpaw_utils import forms
from django.forms.formsets import DELETION_FIELD_NAME

from pbs.stakeholder.models import (Notification,)
import pbs.widgets
from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)

class NotificationCleanMixin(object):
    pass


class NotificationConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Notification,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(Notification,"id",field_class=forms.fields.IntegerField)
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            'notified.edit':forms.widgets.DateInput(attrs={"style":"width:115px"}),
            'contacted.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            'address.edit':forms.widgets.Textarea(attrs={"class":"vTextField","style":"height:53px"}),
            "id.edit":forms.widgets.Hidden(),
            "delete.view":forms.widgets.HyperlinkFactory("id","stakeholder:prescription_notification_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }
        labels = {
            "delete":""
        }


class NotificationMemberUpdateForm(NotificationCleanMixin,NotificationConfigMixin,forms.ListMemberForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") \
           and not self.cleaned_data.get("notified") \
           and not self.cleaned_data.get("contacted") \
           and not self.cleaned_data.get("organisation") \
           and not self.cleaned_data.get("address") \
           and not self.cleaned_data.get("phone")

    class Meta:
        model = Notification
        all_fields = ("id",'notified','contacted',"organisation","address","phone","delete")
        editable_fields = ('id',"notified","contacted","organisation","address","phone")


NotificationListUpdateForm = forms.listupdateform_factory(NotificationMemberUpdateForm,min_num=0,max_num=100,extra=1,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=True)
        
class NotificationBaseListForm(NotificationConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))


class NotificationListForm(NotificationBaseListForm):
    class Meta:
        model = Notification
        all_fields = ("id",'notified','contacted',"organisation","address","phone")
