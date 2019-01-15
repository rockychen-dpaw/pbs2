
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Context,ContextRelevantAction)
from pbs.risk.forms import (ContextUpdateForm,)
from dpaw_utils.views import (OneToOneUpdateView,)

class ContextUpdateView(OneToOneUpdateView):
    title = "Risk management context statement"
    pmodel = Prescription
    model = Context
    form_class = ContextUpdateForm
    context_pobject_name = "prescription"
    one_to_one_field_name = "prescription"
    urlpattern = "context/prescription/<int:ppk>/"
    urlname = "context_update"
    template_name_suffix = "_update"

    def get_success_url(self):
        return urls.reverse("risk:context_update",args=(self.pobject.id,))
    """
    def post(self,*args,**kwargs):
        import ipdb;ipdb.set_trace()
        return super().post(*args,**kwargs)
    """


    def get_context_data(self, **kwargs):
        context = super(ContextUpdateView,self).get_context_data(**kwargs)
        context['relevant_actions'] = ContextRelevantAction.objects.filter(action__risk__prescription__id=self.pobject.id).select_related('action', 'action__risk')
        context["documents"] = self.pobject.document_set.filter(tag__name="Context Map")
        return context

