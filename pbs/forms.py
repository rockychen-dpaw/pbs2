from django import forms
from django.contrib.auth.models import User

from dpaw_utils import forms

class FormActions(object):
    ACTIONS = {
        "save":forms.widgets.HtmlTag("button",{"class":"btn btn-primary btn-success","type":"submit","value":"save","name":"_save"},"Save"),
        "back":forms.widgets.HtmlTag("button",{"class":"btn btn-danger","onclick":"history.go(-1)","id":"id_cancel_button"},"Cancel"),
        "update_selection":forms.widgets.HtmlTag("button",{"class":"btn btn-success btn-block","type":"submit","value":"search"},"Update selection")
    }


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

