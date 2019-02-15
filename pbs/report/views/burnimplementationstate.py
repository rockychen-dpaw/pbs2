from django.http.response import (HttpResponseBadRequest,)
from django import urls


from dpaw_utils.views import (OneToOneUpdateView,AjaxRequestMixin)

from pbs.report.models import (BurnImplementationState,)
from pbs.report.forms import (BurnImplementationStateUpdateForm,BurnImplementationStateViewForm)
from pbs.prescription.models import (Prescription,)
from pbs import mutex, SemaphoreException

class BurnImplementationStateUpdateView(AjaxRequestMixin,OneToOneUpdateView):
    pmodel = Prescription
    model = BurnImplementationState
    context_pobject_name = "prescription"
    one_to_one_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/summary/day/"
    urlname = "prescription_day_state_update"

    title = "Part B Summary ‐ Burn Implementation Plan"
    template_name_suffix = "_form"

    def get_form_class(self):
        if self.pobject.is_draft or self.request.user.has_perms('prescription','can_admin'):
            return BurnImplementationStateUpdateForm
        else:
            return BurnImplementationStateViewForm

    def get_form_kwargs(self):
        kwargs = super(BurnImplementationStateUpdateView,self).get_form_kwargs()
        if self.request.is_ajax():
            submit_field = self.request.POST.get("submit_field")
            if not submit_field:
                raise Exception("submit_field is missing")
            kwargs["editable_fields"] = [submit_field]
        return kwargs

    def update_context_data(self,context):
        super(BurnImplementationStateUpdateView,self).update_context_data(context)
        context["download_pdf"] = urls.reverse("prescription:prescription_download",kwargs={"pk":self.pobject.id})

    def post_ajax(self,request,ppk,*args,**kwargs):
        form = self.get_form_class()(**self.get_form_kwargs())
        if form.is_valid():
            form.save()
            return {}
        else:
            return {"errors":form.errors}
