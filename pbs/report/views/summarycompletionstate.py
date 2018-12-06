from django.http.response import (HttpResponseBadRequest,)
from django import urls


from dpaw_utils.views import (OneToOneUpdateView,AjaxRequestMixin)

from pbs.report.models import (SummaryCompletionState,)
from pbs.report.forms import (SummaryCompletionStateUpdateForm,SummaryCompletionStateViewForm)
from pbs.prescription.models import (Prescription,)
from pbs import mutex, SemaphoreException

class SummaryCompletionStateUpdateView(AjaxRequestMixin,OneToOneUpdateView):
    pmodel = Prescription
    model = SummaryCompletionState
    context_pobject_name = "prescription"
    one_to_one_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/summary/"
    urlname = "prescription_pre_state_update"

    title = "Part A Summary ‐ Summary and Approval"
    template_name_suffix = "_form"

    def get_form_class(self):
        if self.pobject.is_draft or self.request.user.has_perms('prescription','can_admin'):
            return SummaryCompletionStateUpdateForm
        else:
            return SummaryCompletionStateViewForm

    def get_form_kwargs(self):
        kwargs = super(SummaryCompletionStateUpdateView,self).get_form_kwargs()
        if self.request.is_ajax():
            submit_field = self.request.POST.get("submit_field")
            if not submit_field:
                raise Exception("submit_field is missing")
            kwargs["editable_fields"] = [submit_field]
        return kwargs

    def get_context_data(self,**kwargs):
        context_data = super(SummaryCompletionStateUpdateView,self).get_context_data(**kwargs)
        context_data["download_pdf"] = urls.reverse("prescription:prescription_download",kwargs={"pk":self.pobject.id})
        return context_data

    def post_ajax(self,request,ppk,*args,**kwargs):
        form = self.get_form_class()(**self.get_form_kwargs())
        if form.is_valid():
            form.save()
            return {}
        else:
            return {"errors":form.errors}
