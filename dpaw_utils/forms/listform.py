import collections

from django import forms as django_forms
from django.forms.utils import ErrorList
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms.renderers import get_default_renderer
from django.utils.html import mark_safe

from . import forms
from . import boundfield
from . import fields


class ListDataForm(django_forms.BaseForm,collections.Iterable):
    def __init__(self,listform, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None):
        self.listform = listform
        self.is_bound = data is not None or files is not None
        self.files = {} if files is None else files
        self.auto_id = auto_id
        if prefix is not None:
            self.prefix = prefix
        self.error_class = error_class
        # Translators: This is the default suffix added to form field labels
        self.label_suffix = label_suffix if label_suffix is not None else _(':')
        self.empty_permitted = empty_permitted
        self._errors = None  # Stores the errors after clean() has been called.

        # The base_fields class attribute is the *class-wide* definition of
        # fields. Because a particular *instance* of the class might want to
        # alter self.fields, we create self.fields here by copying base_fields.
        # Instances should always modify self.fields; they should not modify
        # self.base_fields.
        if use_required_attribute is not None:
            self.use_required_attribute = use_required_attribute

        # Initialize form renderer. Use a global default if not specified
        # either as an argument or as self.default_renderer.
        if renderer is None:
            if self.default_renderer is None:
                renderer = get_default_renderer()
            else:
                renderer = self.default_renderer
                if isinstance(self.default_renderer, type):
                    renderer = renderer()
        self.renderer = renderer

    @property
    def fields(self):
        return self.listform.fields

    @property
    def instance(self):
        return self.listform.instance

    @instance.setter
    def instance(self,value):
        pass

    @property
    def initial(self):
        return self.listform.initial

    @initial.setter
    def initial(self,value):
        pass

    @property
    def data(self):
        return self.listform.data

    @data.setter
    def data(self,value):
        pass

    @property
    def pk(self):
        return self.initial.pk

    @property
    def is_bound(self):
        return self.listform.is_bound

    def __getitem__(self, name):
        return self.listform.__getitem__(name)

    @is_bound.setter
    def is_bound(self,value):
        pass

    def __iter__(self):
        self._index = -1
        return self

    def __next__(self):
        self._index += 1
        if self._index >= len(self.listform._meta.ordered_fields):
            raise StopIteration()
        else:
            return self.listform[self.listform._meta.ordered_fields[self._index]]

    def as_table(self):
        "Return this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row='<td %(html_class_attr)s>%(field)s</td>',
            error_row='',
            row_ender='</td>',
            help_text_html='<br /><span class="helptext">%s</span>',
            errors_on_separate_row=False)


class ListModelFormMetaclass(forms.BaseModelFormMetaclass,collections.Iterable.__class__):
    """
    Support list reslated features
    1. toggleable_fields to declare toggleable fields
    2. default_toggled_fields to declare default toggled fields
    """
    
    def __new__(mcs, name, bases, attrs):
        if 'Meta' in attrs :
            for item,default_value in [('asc_sorting_html_class','headerSortUp'),('desc_sorting_html_class','headerSortDown'),('sorting_html_class','headerSortable'),
                    ('toggleable_fields',None),('default_toggled_fields',None),('sortable_fields',None)]:
                if not hasattr(attrs['Meta'],item):
                    config = forms.BaseModelFormMetaclass.meta_item_from_base(bases,item)
                    if config:
                        setattr(attrs['Meta'],item,config)
                    else:
                        setattr(attrs['Meta'],item,default_value)

        new_class = super(ListModelFormMetaclass, mcs).__new__(mcs, name, bases, attrs)
        meta = getattr(new_class,"Meta") if hasattr(new_class,"Meta") else None
        opts = getattr(new_class,"_meta") if hasattr(new_class,"_meta") else None
        if not opts or not meta:
            return new_class

        for item in ['asc_sorting_html_class','desc_sorting_html_class','sorting_html_class','toggleable_fields','default_toggled_fields','sortable_fields']:
            if hasattr(meta,item) :
                setattr(opts,item,getattr(meta,item))
            else:
                setattr(opts,item,None)

        model = opts.model
        model_field = None

        if opts.toggleable_fields:
            for field in opts.toggleable_fields:
                field = field.lower()
                classes = getattr(new_class.base_fields[field],"css_classes") if hasattr(new_class.base_fields[field],"css_classes") else []
                classes.append("{}".format(field))
                """
                if field not in classes:
                    classes.append(field)
                """
                if opts.default_toggled_fields and field not in opts.default_toggled_fields:
                    classes.append("hide")
                setattr(new_class.base_fields[field],"css_classes",classes)

        #if has a class initialization method, then call it
        if hasattr(new_class,"_init_class"):
            getattr(new_class,"_init_class")()
                
        return new_class

class BoundFieldIterator(collections.Iterable):
    def __init__(self,form):
        self.form = form
        self._index = None
        self._length = len(self.form._meta.ordered_fields)

    def __iter__(self):
        self._index = -1
        return self

    def __next__(self):
        self._index += 1
        if self._index >= self._length:
            raise StopIteration()
        else:
            return self.form[self.form._meta.ordered_fields[self._index]]

class ToggleableFieldIterator(collections.Iterable):
    def __init__(self,form):
        self.form = form
        self._index = None
        self._toggleable_fields = self.form._meta.toggleable_fields if hasattr(self.form._meta,"toggleable_fields") else None

    def __iter__(self):
        self._index = -1
        return self

    def __next__(self):
        self._index += 1
        if self._toggleable_fields and self._index < len(self._toggleable_fields):
            return self.form[self._toggleable_fields[self._index]]
        else:
            raise StopIteration()


class ListForm(forms.ActionMixin,forms.RequestUrlMixin,forms.ModelFormMetaMixin,django_forms.models.BaseModelForm,collections.Iterable,metaclass=ListModelFormMetaclass):
    """
    Use a form to display list data 
    """

    def __init__(self,data_list=None,instance_list=None,**kwargs):
        if "data" in kwargs:
            del kwargs["data"]

        super(ListForm,self).__init__(**kwargs)

        self.data_list = data_list
        self.instance_list = instance_list
        #set index to one position before the start position. because we need to call next() before getting the first data 
        self.index = None
        self.dataform = ListDataForm(self)

    @property
    def boundfieldlength(self):
        return len(self._meta.ordered_fields)

    @property
    def boundfields(self):
        return BoundFieldIterator(self)

    @property
    def toggleablefields(self):
        if hasattr(self._meta,"toggleable_fields") and self._meta.toggleable_fields:
            return ToggleableFieldIterator(self)
        else:
            return None

    @property
    def model_name_lower(self):
        return self._meta.model.__name__.lower()

    @property
    def model_name(self):
        return self._meta.model.__name__

    @property
    def model_verbose_name(self):
        return self._meta.model._meta.verbose_name;

    @property
    def model_verbose_name_plural(self):
        return self._meta.model._meta.verbose_name_plural;

    @property
    def instance(self):
        if self.index < 0:
            return None
        elif self.instance_list and self.index < len(self.instance_list):
            return self.instance_list[self.index]
        else:
            return None

    @instance.setter
    def instance(self,value):
        pass

    @property
    def initial(self):
        if self.index < 0:
            return {}
        elif self.instance_list and self.index < len(self.instance_list):
            return self.instance_list[self.index]
        else:
            return {}

    @initial.setter
    def initial(self,value):
        pass

    @property
    def data(self):
        if self.index < 0:
            return None
        elif self.data_list and self.index < len(self.data_list):
            return self.data_list[self.index]
        else:
            return None

    @data.setter
    def data(self,value):
        pass

    @property
    def is_bound(self):
        return self.data_list is not None

    @is_bound.setter
    def is_bound(self,value):
        pass

    @property
    def toggleable_fields(self):
        return self._meta.toggleable_fields
    
    def __len__(self):
        if self.data_list:
            return len(self.data_list)
        elif self.instance_list:
            return len(self.instance_list)
        else:
            return 0

    @property
    def first(self):
        self.index = 0
        return self.dataform

    def __iter__(self):
        self.index = -1
        return self

    def __next__(self):
        self.index += 1
        if self.data_list:
            if self.index < len(self.data_list):
                return self.dataform
            else:
                raise StopIteration()
        elif self.instance_list:
            if self.index < len(self.instance_list):
                return self.dataform
            else:
                raise StopIteration()
        else:
            raise StopIteration()


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

    def as_table(self):
        raise NotImplementedError()


            

