
from ..models import (Prescription,RegionalObjective)
from ..forms import (RegionalObjectiveListForm,)
from dpaw_utils import views

class PrescriptionObjectiveUpdateView(views.ManyToManyListView):
    title = "Select Regional Fire Management Plan Objectives"
    pmodel = Prescription
    model = RegionalObjective
    listform_class = RegionalObjectiveListForm
    context_pobject_name = "prescription"
    many_to_many_field_name = "prescription"
    urlpattern = "/prescription/<int:ppk>/add/objectives/"
    urlname = "prescription_objectives_update"
    template_name_suffix = "_list"

    def get_context_data(self,**kwargs):
        context_data = super().get_context_data(**kwargs)
        qs = self.model.objects.filter(region=self.pobject.region.id).exclude(prescription=self.pobject)
        context_data["unselectedlistform"] = self.get_listform_class()(instance_list=qs,request=self.request,requesturl = self.requesturl)
        context_data["object_list_length"] = len(qs) + len(self.object_list)
        return context_data
