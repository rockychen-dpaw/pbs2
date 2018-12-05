from django.forms import formsets
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import DELETION_FIELD_NAME

class BaseFormSet(formsets.BaseFormSet):
    def __init__(self,instances=None,*args,**kwargs):
        super(BaseFormSet,self).__init__(*args,**kwargs)
        self.instances = instances

    def get_form_kwargs(self, index):
        kwargs = super(BaseFormSet,self).get_form_kwargs(index)
        if self.instances and index < len(self.instances):
            if self.is_bound:
                kwargs["instance"] = self.get_instance(index)
            else:
                kwargs["instance"] = self.instances[index]
        return kwargs

    def get_form_field_name(self,index,field_name):
        prefix = self.add_prefix(index)
        return '{}-{}'.format(prefix, field_name) 

    def get_instance(self,index):
        if self.primary_field:
            name = self.get_form_field_name(index,self.primary_field)
            value = self.data.get(name)
            value = self.form.fields[self.primary_field].clean(value,None)
            if value:
                for instance in self.instances:
                    if value == getattr(instance,self.primary_field):
                        return value
                raise ObjectDoesNotExist("{}({}) doesn't exist".format(self.form.model_verbose_name,value))
            else:
                return None
        elif index < len(self.instances):
            return self.instances[index]
        else:
            return None

    def _should_delete_form(self,form):
        """Return whether or not the form was marked for deletion."""
        if hasattr(form,"can_delete"):
            should_delete = form.can_delete
        else:
            should_delete = super(BaseFormSet,self)._should_delete_form(form)
        form.cleaned_data[DELETION_FIELD_NAME] = should_delete
        return should_delete

def formset_factory(form, formset=BaseFormSet, extra=1, can_order=False,
                    can_delete=False, max_num=None, validate_max=False,
                    min_num=None, validate_min=False,primary_field=None):

    cls = formsets.formset_factory(form,formset=formset,extra=extra,can_order=can_order,can_delete=can_delete,max_num=max_num,validate_max=validate_max,min_num=min_num,validate_min=validate_min)
    cls.primary_field = primary_field
    return cls


