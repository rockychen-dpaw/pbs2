from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (Contingency,)
from pbs.risk.forms.contingencyaction import (ContingencyActionListForm,ContingencyActionListOnlyForm)
from pbs.risk.forms.contingencynotification import (ContingencyNotificationListForm,ContingencyNotificationListOnlyForm)

from dpaw_utils import forms

class ContingencyCleanMixin(object):
    pass

EditableIntegratedActionsField = forms.fields.ConditionalMultipleFieldFactory(Contingency,"actions_migrated",("old_actions","actions","add_action"),
    view_layouts=[
        (lambda f:f.value() == False,('{0}{1}<div style="margin:4px"><i class="icon-plus"></i>{2}</div>',("old_actions","actions","add_action"),False)),
        (lambda f:True,('{0}<div style="margin:4px"><i class="icon-plus"></i>{1}</div>',("actions","add_action"),False))
    ]
)

IntegratedActionsField = forms.fields.ConditionalMultipleFieldFactory(Contingency,"actions_migrated",("old_actions","actions"),
    view_layouts=[
        (lambda f:f.value() == False,('{0}{1}',("old_actions","actions"),False)),
        (lambda f:True,('{0}',("actions",),False))
    ]
)

EditableIntegratedNotificationsField = forms.fields.ConditionalMultipleFieldFactory(Contingency,"notifications_migrated",("old_notifications","notifications","add_notification"),
    view_layouts=[
        (lambda f:f.value() == False,('{0}{1}<div style="margin:4px"><i class="icon-plus"></i>{2}</div>',("old_notifications","notifications","add_notification"),False)),
        (lambda f:True,('{0}<div style="margin:4px"><i class="icon-plus"></i>{1}</div>',("notifications","add_notification"),False))
    ]
)

IntegratedNotificationsField = forms.fields.ConditionalMultipleFieldFactory(Contingency,"notifications_migrated",("old_notifications","notifications"),
    view_layouts=[
        (lambda f:f.value() == False,('{0}{1}',("old_notifications","notifications"),False)),
        (lambda f:True,('{0}',("notifications",),False))
    ]
)

class ContingencyConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Contingency,"id",forms.fields.IntegerField,field_params={"required":False}),
            "old_actions":forms.fields.Field,
            "old_notifications":forms.fields.Field,
            "actions":forms.fields.Field,
            "notifications":forms.fields.Field,
            "integrated_actions.list":EditableIntegratedActionsField,
            "integrated_actions.listonly":IntegratedActionsField,
            "integrated_notifications.list":EditableIntegratedNotificationsField,
            "integrated_notifications.listonly":IntegratedNotificationsField,
            "delete":forms.fields.AliasFieldFactory(Contingency,"id",field_class=forms.fields.IntegerField),
            "add_action":forms.fields.CharField,
            "add_notification":forms.fields.CharField,
        }
        labels = {
            "delete":"",
            "actions":"Actions",
            "integrated_actions":"Actions",
            "integrated_notifications":"Notifications",
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.HiddenInput(),
            "actions_migrated.view":forms.widgets.ImgBooleanDisplay(),
            "old_actions.view":forms.widgets.ListDisplayFactory(forms.widgets.TextDisplay,template="""
            <div class="alert alert-warning" style="padding:4px;margin-bottom:0px"><strong>Old actions list:</strong>
            <ul>
                {% for widget in widgets %}
                <li>{{widget}}</li>
                {% endfor %}
            </ul>
            </div>

            """),
            "actions.list":forms.widgets.ModelListDisplayFactory(ContingencyActionListForm,styles={"tbody-td":"white-space:pre-wrap"}),
            "actions.listonly":forms.widgets.ModelListDisplayFactory(ContingencyActionListOnlyForm,styles={"li":"white-space:pre-wrap"},use_table=False),
            "notifications.list":forms.widgets.ModelListDisplayFactory(ContingencyNotificationListForm,styles={"tbody-td":"white-space:pre-wrap"}),
            "notifications.listonly":forms.widgets.ModelListDisplayFactory(ContingencyNotificationListOnlyForm,styles={"tbody-td":"white-space:pre-wrap"}),
            "old_notifications.list":forms.widgets.ModelListDisplayFactory(ContingencyNotificationListOnlyForm,
                styles={"tbody-td":"white-space:pre-wrap","table":"background-color:#fcf8e3","tbody-td":"background-color:#fcf8e3","title":"background-color:#fcf8e3;font-weight:bold"},
                title="Old Notifications"),
            "notifications_migrated.view":forms.widgets.ImgBooleanDisplay(),
            "description.list":forms.widgets.HyperlinkFactory("description","risk:prescription_contingency_update",ids=[("id","pk"),("prescription","ppk")]),
            "add_action.view":forms.widgets.HyperlinkFactory("add_action","risk:contingency_action_create",ids=[("id","ppk")],widget_class=None,template="""
            <a href='{url}'>Add an action</a>
            """),
            "add_notification.view":forms.widgets.HyperlinkFactory("add_notification","risk:contingency_notification_create",ids=[("id","ppk")],widget_class=None,template="""
            <a href='{url}'>Add a notification</a>
            """),
            "delete.view":forms.widgets.HyperlinkFactory("id","risk:prescription_contingency_delete_confirm",ids=[("id","pk"),("prescription","ppk")],querystring="nexturl={nexturl}",parameters=[("request_full_path","nexturl")],template="<img title='Delete' onclick='window.location=\"{url}\"' src='/static/img/delete.png' style='width:16px;height:16px;cursor:pointer'>")
        }

class ContingencyBaseForm(ContingencyCleanMixin,ContingencyConfigMixin,forms.ModelForm):
    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance

    class Meta:
        pass

class ContingencyCreateForm(ContingencyBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = Contingency
        purpose = ("edit","view")
        all_fields = ("description","trigger")
        editable_fields = all_fields

class ContingencyUpdateForm(ContingencyBaseForm):
    all_buttons = [
        BUTTON_ACTIONS["save"],
        BUTTON_ACTIONS["back"]
    ]
    class Meta:
        model = Contingency
        purpose = ("edit","view")
        all_fields = ("description","trigger","actions_migrated","notifications_migrated")
        editable_fields = ("description","trigger")

class ActionMigratedContingencyUpdateForm(ContingencyUpdateForm):
    class Meta:
        editable_fields = ("description","trigger","notifications_migrated")

class NotificationMigratedContingencyUpdateForm(ContingencyUpdateForm):
    class Meta:
        editable_fields = ("description","trigger","actions_migrated")

class UnmigratedContingencyUpdateForm(ContingencyUpdateForm):
    class Meta:
        editable_fields = ("description","trigger","actions_migrated","notifications_migrated")

class ContingencyBaseListForm(ContingencyConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ContingencyListForm(ContingencyBaseListForm):
    class Meta:
        model = Contingency
        all_fields = ("description","trigger","integrated_actions","old_actions","actions","add_action","integrated_notifications","old_notifications","notifications","add_notification","delete")
        widths = {
            "delete":"16px",
            "notifications":"330px"
        }
        editable_fields = []
        ordered_fields = ("description","trigger","integrated_actions","integrated_notifications","delete")

class ContingencyDeleteListForm(ContingencyBaseListForm):

    class Meta:
        model = Contingency
        purpose = (None,('listonly','list','view'))
        all_fields = ("description","trigger","integrated_actions","old_actions","actions","integrated_notifications","old_notifications","notifications","actions_migrated","notifications_migrated")
        editable_fields = []
        ordered_fields = ("description","trigger","integrated_actions","integrated_notifications","actions_migrated","notifications_migrated")

