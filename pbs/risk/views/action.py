from django.urls import path 
from django import urls

from pbs.prescription.models import (Prescription,)
from pbs.risk.models import (Action,Risk,categorylist,Treatment)
from pbs.risk.forms import (ActionListUpdateForm,PreburnActionListUpdateForm,DayofburnActionListUpdateForm,PostburnActionListUpdateForm,ActionListForm,ActionFilterForm,
        MultipleActionCreateForm,ActionUpdateForm,
        TreatmentListForm)
from pbs.risk.filters import (ActionFilter,)
from dpaw_utils import views
import pbs.forms

class PrescriptionMultipleActionCreateView(pbs.forms.GetActionMixin,views.OneToManyCreateView):
    title = "Add Plan Action"
    pmodel = Prescription
    model = Action
    form_class = MultipleActionCreateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/<int:actionpk>/add/multiple/"
    urlname = "prescription_multipleaction_add"
    template_name_suffix = "_multiple_add"

    def get(self,request,ppk,actionpk,**kwargs):
        self.baseaction = Action.objects.get(id = actionpk)
        return super().get(request,ppk,actionpk,**kwargs)

    def post(self,request,ppk,actionpk,**kwargs):
        self.baseaction = Action.objects.get(id = actionpk)
        return super().post(request,ppk,actionpk,**kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['baseaction'] = self.baseaction
        return kwargs

    def _get_success_url(self):
        return urls.reverse("risk:prescription_action_changelist",args=(self.object.risk.prescription.id,))

class PrescriptionActionUpdateView(pbs.forms.GetActionMixin,views.OneToManyUpdateView):
    title = "Change Plan Action"
    pmodel = Prescription
    model = Action
    form_class = ActionUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/<int:pk>/"
    urlname = "prescription_action_update"
    template_name_suffix = "_update"

    def _get_success_url(self):
        return urls.reverse("risk:prescription_action_changelist",args=(self.object.risk.prescription.id,))

class PrescriptionActionsUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Plan Actions"
    pmodel = Prescription
    model = Action
    filter_class = ActionFilter
    filterform_class = ActionFilterForm
    listform_class = ActionListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/"
    urlname = "prescription_action_changelist"
    filtertool = False
    default_order = ("risk__category__name","risk__name","index")


    @property
    def deleteconfirm_url(self):
        return urls.reverse("risk:prescription_actions_delete",args=(self.pobject.id,))

    @classmethod
    def _get_extra_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        return [
            path('prescription/<int:ppk>/action/<int:pk>/deleteconfirm', cls.as_view(),{"action":"deleteconfirm"},name='prescription_action_delete_confirm'),
            path('prescription/<int:ppk>/actions/delete', cls.as_view(),{"action":"deleteconfirmed"},name='prescription_actions_delete'),
        ]

    def _get_success_url(self):
        return urls.reverse("risk:prescription_action_changelist",args=(self.pobject.id,))

    def get_listform_class(self):
        if self.action == 'deleteconfirm':
            return ActionListForm
        else:
            return super().get_listform_class()

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["relevantlist"] = ((True,"Yes"),(False,"No"))
        context["categorylist"] = categorylist

        return context


class PrescriptionPreBurnActionsUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Pre-burn Actions"
    pmodel = Prescription
    model = Action
    listform_class = PreburnActionListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/preburn/"
    urlname = "prescription_preburn_action_changelist"
    default_order = ("risk__category__name","risk__name","index")
    template_name_suffix = "_preburn_changelist"


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pre_burn=True)

    def _get_success_url(self):
        return urls.reverse("risk:prescription_preburn_action_changelist",args=(self.pobject.id,))

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.pobject.document_set.filter(tag__id=171)

        return context

class PrescriptionDayOfBurnActionsUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Day of Burn Actions"
    pmodel = Prescription
    model = Action
    listform_class = DayofburnActionListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/dayofburn/"
    urlname = "prescription_dayofburn_action_changelist"
    default_order = ("risk__category__name","risk__name","index")
    template_name_suffix = "_dayofburn_changelist"


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(day_of_burn=True)

    def _get_success_url(self):
        return urls.reverse("risk:prescription_dayofburn_action_changelist",args=(self.pobject.id,))

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.pobject.document_set.filter(tag__id=184)
        context["treatmentlistform"] = TreatmentListForm(instance_list=Treatment.objects.filter(register__prescription = self.pobject),request=self.request,requesturl = self.requesturl)

        return context

class PrescriptionPostBurnActionsUpdateView(pbs.forms.GetActionMixin,views.OneToManyListUpdateView):
    title = "Post Burn Actions"
    pmodel = Prescription
    model = Action
    listform_class = PostburnActionListUpdateForm
    context_pobject_name = "prescription"
    one_to_many_field_name = "risk__prescription"
    urlpattern = "prescription/<int:ppk>/action/postburn/"
    urlname = "prescription_postburn_action_changelist"
    default_order = ("risk__category__name","risk__name","index")
    template_name_suffix = "_postburn_changelist"


    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(post_burn=True)

    def _get_success_url(self):
        return urls.reverse("risk:prescription_postburn_action_changelist",args=(self.pobject.id,))

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["documents"] = self.pobject.document_set.filter(tag__id=189)

        return context

