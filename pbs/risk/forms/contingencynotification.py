from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (ContingencyNotification,)

from dpaw_utils import forms

class ContingencyNotificationCleanMixin(object):
    pass

class ContingencyNotificationConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(ContingencyNotification,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(ContingencyNotification,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "id.edit":forms.widgets.HiddenInput(),
            'name.edit':forms.widgets.Textarea(attrs={"class":"vTextField"}),
            "name.list":forms.widgets.HyperlinkFactory("notification","risk:contingency_notification_update",ids=[("id","pk"),("contingency","ppk")]),
            'location.edit':forms.widgets.TextInput(attrs={"class":"vTextField"}),
            'organisation.edit':forms.widgets.TextInput(attrs={"class":"vTextField"}),
            'contact_number.edit':forms.widgets.TextInput(attrs={"class":"vTextField"}),
            "delete.view":forms.widgets.HyperlinkFactory("id","risk:contingency_notification_delete_confirm",ids=[("id","pk"),("contingency","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<img title='Delete' onclick='window.location=\"{url}\"' src='/static/img/inlinedelete.png' style='width:12px;height:12px;cursor:pointer'>")
        }

class ContingencyNotificationBaseForm(ContingencyNotificationCleanMixin,ContingencyNotificationConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.contingency = parent_instance

    class Meta:
        pass

class ContingencyNotificationCreateForm(ContingencyNotificationBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = ContingencyNotification
        purpose = ("edit","view")
        all_fields = ("name","location","organisation","contact_number")
        editable_fields = all_fields

class ContingencyNotificationUpdateForm(ContingencyNotificationBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = ContingencyNotification
        purpose = ("edit","view")
        all_fields = ("name","location","organisation","contact_number")
        editable_fields = all_fields

class ContingencyNotificationBaseListForm(ContingencyNotificationConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ContingencyNotificationListForm(ContingencyNotificationBaseListForm):
    class Meta:
        model = ContingencyNotification
        all_fields = ("name","location","organisation","contact_number","delete")
        widths = {
            "delete":"16px",
            "name":"60px",
            "location":"60px",
            "organisation":"100px",
            "contact_number":"80px",
        }
        editable_fields = []

class ContingencyNotificationListOnlyForm(ContingencyNotificationBaseListForm):
    class Meta:
        model = ContingencyNotification
        purpose = (None,('listonly','list','view'))
        all_fields = ("name","location","organisation","contact_number")
        widths = {
            "name":"150px",
            "location":"300px",
            "organisation":"100px",
            "contact_number":"100px",
        }
        editable_fields = []
        ordered_fields = all_fields

