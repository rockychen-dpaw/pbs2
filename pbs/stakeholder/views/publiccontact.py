from django import urls
from django.urls import path 

from pbs.stakeholder.models import (PublicContact,)
from pbs.stakeholder.forms import (PublicContactListUpdateForm,PublicContactListForm)
from dpaw_utils.views import (OneToManyListUpdateView,)
from pbs.prescription.models import (Prescription,)
import pbs.forms

class PrescriptionPublicContactListUpdateView(pbs.forms.GetActionMixin,OneToManyListUpdateView):
    model=PublicContact
    listform_class = PublicContactListUpdateForm
    urlpattern = "prescription/<int:ppk>/publiccontact/"
    urlname = "prescription_publiccontact_changelist"
    one_to_many_field_name = "prescription"
    pmodel = Prescription
    ppk_url_kwarg = "ppk"
    context_pobject_name = "prescription"
    title = "Public Contacts"

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/publiccontact/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_publiccontact_delete_confirm'),
            path('prescription/<int:ppk>/publiccontacts/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_publiccontacts_delete'),
        ]

    @property
    def deleteconfirm_url(self):
        return urls.reverse("stakeholder:prescription_publiccontacts_delete",args=(self.pobject.id,))

    def _get_success_url(self):
        return urls.reverse("stakeholder:prescription_publiccontact_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return PublicContactListForm
        else:
            return super().get_listform_class()


