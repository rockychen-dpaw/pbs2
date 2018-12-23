from django import forms
from django.contrib.auth.models import User

from dpaw_utils import forms

BUTTON_ACTIONS = {
    "save":forms.Action("save","button","Save",{"class":"btn btn-primary btn-success","type":"submit"}),
    "select":forms.Action("select","button","Select",{"class":"btn btn-primary btn-success","type":"submit",}),
    "back":forms.Action("back","a","Cancel",{"class":"btn btn-danger","onclick":"history.go(-1);"}),
    "update_selection":forms.Action("search","button","Update Selection",{"class":"btn btn-success btn-block","type":"submit","style":"width:260px"}),
    "upload":forms.Action("upload","button","Upload",{"class":"btn btn-success","type":"submit"}),
    "download":forms.Action("download","button","Download",{"class":"btn btn-success btn-block","type":"submit","style":"width:260px"}),
    "deleteconfirm":forms.Action("delete","button","Delete",{"class":"btn btn-success btn-block","type":"submit","style":"width:260px"}),
    "deleteconfirmed":forms.Action("delete","button","Delete",{"class":"btn btn-success btn-block","type":"submit","style":"width:260px"}),

}

OPTION_ACTIONS = {
    "delete_selected_epfp":forms.Action("delete_selected","option","Delete selected Prescribed Fire Plans"),
    "export_to_csv":forms.Action("export_to_csv","option","Export to CSV"),
    "burn_summary_to_csv":forms.Action("burn_summary_to_csv","option","Export Burn Summary to CSV"),
    "delete_approval_endorsement":forms.Action("delete_approval_endorsement","option","Remove Burn Plan Endorsements and Approval"),
    "carry_over_burns":forms.Action("carry_over_burns","option","Carry over burns"),
    "bulk_corporate_approve":forms.Action("bulk_corporate_approve","option","Apply corporate approval")
}

class GetActionMixin(object):
    def get_action(self,action_name):
        return BUTTON_ACTIONS.get(action_name) or OPTION_ACTIONS.get(action_name)


class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['is_active'].label = ("Approved User (i.e. enable login "
                                          "for this user?)")
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and not instance.profile.is_fpc_user():
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['first_name'].widget.attrs['readonly'] = True
            self.fields['last_name'].widget.attrs['readonly'] = True

    class Meta:
        model = User
        fields = ('is_active', 'groups')

