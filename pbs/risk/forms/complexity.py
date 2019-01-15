from pbs.forms import (BUTTON_ACTIONS,OPTION_ACTIONS)
from pbs.risk.models import (Complexity,)

from dpaw_utils import forms

class ComplexityCleanMixin(object):
    def clean_rationale(self):
        rating = self.cleaned_data.get("rating")
        rationale = self.cleaned_data.get("rationale")
        if rating or rationale:
            if not rating:
                self.add_error("rating",forms.ValidationError('Rating must be set for this purpose as it has been given a rationale.'))
            if not rationale:
                raise forms.ValidationError('Rationale must be set for this purpose as it has been given a rating.')
        return rationale if rationale else ""

class ComplexityConfigMixin(object):
    class Meta:
        field_classes_config = {
            "__default__":forms.fields.CharField,
            "id":forms.fields.OverrideFieldFactory(Complexity,"id",forms.fields.IntegerField,field_params={"required":False}),
            "delete":forms.fields.AliasFieldFactory(Complexity,"id",field_class=forms.fields.IntegerField)
        }
        labels = {
            "delete":"",
            "criteria":"Criteria",
            "sub_factor":"Sub Factor"
        }
        widgets_config = {
            "__default__.view":forms.widgets.TextDisplay(),
            "__default__.edit":forms.widgets.TextInput(),
            "id.edit":forms.widgets.Hidden(),
            'rationale.edit':forms.widgets.Textarea(attrs={"class":"vTextField","rows":3}),
            "delete.view":forms.widgets.HyperlinkFactory("id","prescription:prescription_successcriteria_delete_confirm",ids=[("id","pk"),("prescription","ppk")],template="<button id='delete' title='Delete' onclick='window.location=\"{url}\"' type='button' style='display:none' >Delete</button>")
        }

class ComplexityFilterForm(ComplexityConfigMixin,forms.FilterForm):
    all_buttons = [
    ]

    class Meta:
        model = Complexity
        purpose = ('filter','view')
        all_fields = ('factor',)

class ComplexityMemberUpdateForm(forms.RequestUrlMixin,ComplexityCleanMixin,ComplexityConfigMixin,forms.ListMemberForm):

    def set_parent_instance(self,parent_instance):
        self.instance.prescription = parent_instance


    @property
    def can_delete(self):
        return not self.cleaned_data.get("id") and not self.cleaned_data.get("criteria")

    class Meta:
        model = Complexity
        widths = {
            "criteria":"30%",
        }
        all_fields = ("factor","sub_factor","rating","rationale","id")
        editable_fields = ('id',"rating","rationale")
        ordered_fields = ("id","factor","sub_factor",'rating','rationale')
        sortable_fields = ("rating",)

ComplexityListUpdateForm = forms.listupdateform_factory(ComplexityMemberUpdateForm,min_num=0,max_num=100,extra=0,all_buttons=[BUTTON_ACTIONS.get('back'),BUTTON_ACTIONS.get('save')],can_delete=False,can_add=False)

class ComplexityBaseListForm(ComplexityConfigMixin,forms.ListForm):
    class Meta:
        purpose = (None,('list','view'))

class ComplexityListForm(ComplexityBaseListForm):
    all_buttons = [
        BUTTON_ACTIONS["back"],
        BUTTON_ACTIONS["select"],
    ]
    def __init__(self, *args, **kwargs):
        super(ComplexityListForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Complexity
        all_fields = ("factor","sub_factor","rating","rationale","id")
        widths = {
            "criteria":"30%",
        }
        editable_fields = []
        ordered_fields = ("id","factor","sub_factor",'rating','rationale')

