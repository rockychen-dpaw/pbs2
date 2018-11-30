from django.http.response import (HttpResponseBadRequest,)
from django import urls


from dpaw_utils.views import (OneToOneModelUpdateView,AjaxRequestMixin)

from pbs.report.models import (BurnClosureState,)
from pbs.report.forms import (BurnClosureStateUpdateForm,BurnClosureStateViewForm)
from pbs.prescription.models import (Prescription,)
from pbs import mutex, SemaphoreException

class BurnClosureStateUpdateView(AjaxRequestMixin,OneToOneModelUpdateView):
    pmodel = Prescription
    model = BurnClosureState
    context_pobject_name = "prescription"
    one_to_one_field_name = "prescription"
    urlpattern = "prescription/<int:ppk>/summary/post/"
    urlname = "prescription_post_state_update"

    title = "Part C Summary ‐ Burn Closure and Evaluation "
    template_name_suffix = "_form"

    def get_form_class(self):
        if not self.pobject.is_approved:
            return BurnClosureStateViewForm
        elif not self.pobject.is_closed:
            return BurnClosureStateUpdateForm
        else:
            return BurnClosureStateViewForm

    def get_form_kwargs(self):
        kwargs = super(BurnClosureStateUpdateView,self).get_form_kwargs()
        if self.request.is_ajax():
            submit_field = self.request.POST.get("submit_field")
            if not submit_field:
                raise Exception("submit_field is missing")
            kwargs["editable_fields"] = [submit_field]
        return kwargs

    def get_context_data(self,**kwargs):
        context_data = super(BurnClosureStateUpdateView,self).get_context_data(**kwargs)
        context_data["download_pdf"] = urls.reverse("prescription:prescription_download",kwargs={"pk":self.pobject.id})
        return context_data

    def post_ajax(self,request,ppk,*args,**kwargs):
        form = self.get_form_class()(**self.get_form_kwargs())
        if form.is_valid():
            form.save()
            return {}
        else:
            return {"errors":form.errors}
