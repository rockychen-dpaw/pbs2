from django.forms import formsets
from django.core.exceptions import ObjectDoesNotExist
from django.forms.formsets import DELETION_FIELD_NAME
from django.db import transaction

from . import forms
from .listform import (ToggleableFieldIterator,BoundFieldIterator,ListModelFormMetaclass)
from . import boundfield
from . import fields

class BaseFormSet(formsets.BaseFormSet):
    def __init__(self,parent_instance=None,instance_list=None,*args,**kwargs):
        if "prefix" not in kwargs:
            kwargs["prefix"] = self.__class__.default_prefix
        kwargs['initial']=instance_list
        super(BaseFormSet,self).__init__(*args,**kwargs)
        self.instance_list = instance_list
        self.parent_instance = parent_instance

    def get_form_kwargs(self, index):
        kwargs = super(BaseFormSet,self).get_form_kwargs(index)
        if self.instance_list and index < len(self.instance_list):
            if self.is_bound:
                kwargs["instance"] = self.get_instance(index)
            else:
                kwargs["instance"] = self.instance_list[index]
        if self.parent_instance:
            kwargs["parent_instance"] = self.parent_instance
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
                for instance in self.instance_list:
                    if value == getattr(instance,self.primary_field):
                        return value
                raise ObjectDoesNotExist("{}({}) doesn't exist".format(self.form.model_verbose_name,value))
            else:
                return None
        elif index < len(self.instance_list):
            return self.instance_list[index]
        else:
            return None

    def _should_delete_form(self,form):
        """Return whether or not the form was marked for deletion."""
        should_delete = super(BaseFormSet,self)._should_delete_form(form)
        if not should_delete and hasattr(form,"can_delete"):
            should_delete = form.can_delete
        form.cleaned_data[DELETION_FIELD_NAME] = should_delete
        return should_delete

def formset_factory(form, formset=BaseFormSet, extra=1, can_order=False,
                    can_delete=False, max_num=None, validate_max=False,
                    min_num=None, validate_min=False,primary_field=None):

    cls = formsets.formset_factory(form,formset=formset,extra=extra,can_order=can_order,can_delete=can_delete,max_num=max_num,validate_max=validate_max,min_num=min_num,validate_min=validate_min)
    cls.primary_field = primary_field
    cls.default_prefix = form._meta.model.__name__.lower()
    return cls


class ListUpdateForm(forms.ActionMixin,forms.RequestUrlMixin,forms.RequestMixin,BaseFormSet):
    model_name_lower=None
    model_primary_key = "id"
    @property
    def form_instance(self):
        if len(self) > 0:
            return self[0]
        elif not hasattr(self,"_form_instance"):
            self._form_instance = self.form()
        return self._form_instance

    @property
    def toggleablefields(self):
        obj = self.form_instance
        if hasattr(obj._meta,"toggleable_fields") and obj._meta.toggleable_fields:
            return ToggleableFieldIterator(obj)
        else:
            return None

    @property
    def boundfields(self):
        return BoundFieldIterator(self.form_instance)

    def full_clean(self):
        super().full_clean()
        if not self.is_bound:  # Stop further processing.
            return
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if self.can_delete and self._should_delete_form(form):
                if form._errors:
                    form._errors.clear()
 
    def save(self):
        if not self.is_bound:  # Stop further processing.
            return
        with transaction.atomic():
            for i in range(0, self.total_form_count()):
                form = self.forms[i]
                if self.can_delete and self._should_delete_form(form):
                    if form.instance.pk:
                        form.instance.delete()
                    continue
                form.save()

 


class ListMemberForm(forms.ModelForm,metaclass=ListModelFormMetaclass):
    def __getitem__(self, name):
        """Return a BoundField with the given name."""
        try:
            field = self.fields[name]
        except KeyError:
            raise KeyError(
                "Key '%s' not found in '%s'. Choices are: %s." % (
                    name,
                    self.__class__.__name__,
                    ', '.join(sorted(f for f in self.fields)),
                )
            )
        if name not in self._bound_fields_cache:
            if isinstance(field,fields.CompoundField):
                self._bound_fields_cache[name] = boundfield.CompoundListBoundField(self,field,name)
            else:
                self._bound_fields_cache[name] = boundfield.ListBoundField(self,field,name)
        return self._bound_fields_cache[name]

    @property
    def boundfields(self):
        return BoundFieldIterator(self)

def listupdateform_factory(form, formset=ListUpdateForm, extra=1, can_order=False,
                    can_delete=False, max_num=None, validate_max=False,
                    min_num=None, validate_min=False,primary_field=None,all_actions=None,all_buttons=None):

    cls = formsets.formset_factory(form,formset=formset,extra=extra,can_order=can_order,can_delete=can_delete,max_num=max_num,validate_max=validate_max,min_num=min_num,validate_min=validate_min)
    cls.primary_field = primary_field
    cls.default_prefix = form._meta.model.__name__.lower()
    cls.model_name_lower = form._meta.model.__name__.lower()
    if all_actions:
        cls.all_actions = all_actions
    if all_buttons:
        cls.all_buttons = all_buttons

    cls.template_forms = formsets.formset_factory(form,formset=formset,extra=1,min_num=1,max_num=1)(prefix=cls.default_prefix)
    for field in cls.template_forms[0].fields.values():
        field.required=False

    return cls

