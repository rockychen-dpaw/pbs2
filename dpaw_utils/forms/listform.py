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
        self._iterator = self.listform.fields.keys().__iter__()
        return self

    def __next__(self):
        return self.listform[self._iterator.__next__()]

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
                classes = getattr(new_class.all_base_fields[field],"css_classes") if hasattr(new_class.all_base_fields[field],"css_classes") else []
                classes.append("{}".format(field))
                """
                if field not in classes:
                    classes.append(field)
                """
                if opts.default_toggled_fields and field not in opts.default_toggled_fields:
                    classes.append("hide")
                setattr(new_class.all_base_fields[field],"css_classes",classes)

        #if has a class initialization method, then call it
        if hasattr(new_class,"_init_class"):
            getattr(new_class,"_init_class")()
                
        return new_class

class BoundFieldIterator(collections.Iterable):
    def __init__(self,form):
        self.form = form
        self._iterator = None

    def __iter__(self):
        self._iterator = self.form.fields.keys().__iter__()
        return self

    def __next__(self):
        return self.form[self._iterator.__next__()]

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


class ListForm(forms.ActionMixin,forms.RequestUrlMixin,django_forms.models.BaseModelForm,collections.Iterable,metaclass=ListModelFormMetaclass):
    """
    Use a form to display list data 
    """

    def __init__(self,data_list=None,initial_list=None,**kwargs):
        if "data" in kwargs:
            del kwargs["data"]

        super(ListForm,self).__init__(**kwargs)

        self.data_list = data_list
        self.initial_list = initial_list
        #set index to one position before the start position. because we need to call next() before getting the first data 
        self.index = None
        self.dataform = ListDataForm(self)

    @property
    def boundfields(self):
        return BoundFieldIterator(self)

    @property
    def toggleablefields(self):
        return ToggleableFieldIterator(self)

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
    def initial(self):
        if self.index < 0:
            return {}
        elif self.initial_list and self.index < len(self.initial_list):
            return self.initial_list[self.index]
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
        elif self.initial_list:
            return len(self.initial_list)
        else:
            return 0

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
        elif self.initial_list:
            if self.index < len(self.initial_list):
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


    def toggleable_fields_html(self):
        if self._meta.toggleable_fields:
            #add the javascript file for show/hide column features
            output.append(safe("""
                <script type="text/javascript">
                    var {0}_toggle_columns = new ToggleTableColumn("{0}","#{0}_column_tools button","#{0}_result_list");
                    $(document).ready(function(){{
                        {0}_toggle_columns.init();
                    }})
                </script>
            """.format(self._meta.model.__name__.lower())))

            output.append("""
               <div class="row toggletools" id="{}_column_tools">
                  <div class="span12">
                      <div class="alert alert-info">
                          <strong>Show/Hide Columns</strong><br>
                          <div class="column-tools btn-group" style="white-space:normal;">
            """.format(self._meta.model.__name__.lower()))

            for field in self._meta.toggleable_fields:
                output.append('<button id="toggle-{1}" class="btn btn-small{2}" data-class="{1}">{0}</button>'.format(
                    self[field].label,field.lower(),
                    "" if field not in self._meta.default_toggled_fields else " btn-info"))

            output.append("""
                      </div>
                  </div>
              </div>
            </div>
            """)


    def _html_output(self, list_starter,list_ender,header_starter,header_ender,body_starter,body_ender,row_starter,row_ender,column_header,data_outputer):
        #output the header
        output = []

        #output list table
        output.append(list_starter)
        output.append(header_starter)
        output.append(row_starter)
        #output table header
        for name, field in self.fields.items():
            bf = self[name]
            # Escape and cache in local variable.
            if bf.is_hidden:
                continue
            else:
                if bf.label:
                    label = conditional_escape(bf.label) or ''
                else:
                    label = ''
                html_class_attr = ""
                html_onclick_attr = ""
                if self.url:
                    ordering=""
                    if self._meta.sortable_fields and name in self._meta.sortable_fields:
                        if self.sorting_status:
                            if self.sorting_status[0] == name:
                                if self.sorting_status[1]:
                                    html_class_attr = " headerSortUp"
                                    ordering = "-{}".format(name) 
                                else:
                                    html_class_attr = " headerSortDown"
                                    ordering = name
                            else:
                                html_class_attr = " headerSortable"
                                ordering = name
                        else:
                            html_class_attr = " headerSortable"
                            ordering = name
                    html_onclick_attr = " onclick=\"document.location='{}order_by={}'\"".format(self.url,ordering) if ordering else ""

                if hasattr(field,"css_classes"):
                    html_class_attr = " class='{}{}'".format(" ".join(field.css_classes),html_class_attr)
                elif html_class_attr:
                    html_class_attr = " class='{}'".format(html_class_attr)
                

                output.append(column_header % {
                    'label': label,
                    'html_attr':"{}{}".format(html_class_attr,html_onclick_attr)
                })
        output.append(row_ender)
        output.append(header_ender)
        #output table data
        output.append(body_starter)
        while self.next():
            output.append(row_starter)
            output.append(data_outputer())
            output.append(row_ender)

        output.append(body_ender)
        output.append(list_ender)
        return mark_safe('\n'.join(output))

    def as_table(self):
        "Return list header."
        raise NotImplementedError()
        """
        return self._html_output(
            list_starter='<table id="{}_result_list" class="table table-striped table-condensed table-hober table-fixed-header">'.format(self._meta.model.__name__.lower()),
            list_ender='</table>',
            header_starter="<thead>",
            header_ender="</thead>",
            body_starter="<tbody>",
            body_ender="</tbody>",
            row_starter="<tr>",
            row_ender="</tr>",
            column_header='<th%(html_attr)s style="vertical-align:middle">%(label)s</th>',
            data_outputer=self.dataform.as_table
            )
        """

    class Meta:
        @staticmethod
        def formfield_callback(field,**kwargs):
            if isinstance(field,models.Field):
                form_class = kwargs.get("form_class")
                if form_class:
                    kwargs["choices_form_class"] = form_class
                result = field.formfield(**kwargs)
                if form_class and not isinstance(result,form_class):
                    raise Exception("'{}' don't use the form class '{}' declared in field_classes".format(field.__class__.__name__,form_class.__name__))
            else:
                result = kwargs.pop("form_class")(**kwargs)

            return result

        @classmethod
        def is_dbfield(cls,field_name):
            if "." in field_name:
                return False

            try:
                model_field = cls.model._meta.get_field(field_name)
                return True
            except:
                return False


            

