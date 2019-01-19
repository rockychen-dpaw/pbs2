import inspect
import collections

from django.utils.html import html_safe,conditional_escape,mark_safe
from django.core.exceptions import ValidationError
from django.utils import six
from django import forms
from django.db import models
from django.utils import safestring

from . import widgets
from . import fields

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

class BoundField(forms.boundfield.BoundField):
    def __init__(self, form, field, name):
        self.form_field_name = name
        super(BoundField,self).__init__(form,field,field.field_name if isinstance(field,fields.AliasFieldMixin) else name)
    """ 
    Extend django's BoundField to support the following features
    1. Get extra css_classes from field's attribute 'css_classes'
    """
    def css_classes(self, extra_classes=None):
        if hasattr(self.field,"css_classes"):
            if extra_classes:
                if hasattr(extra_classes, 'split'):
                    extra_classes = extra_classes.split()
                extra_classes += getattr(self.field,"css_classes")
                return super(BoundField,self).css_classes(extra_classes)
            else:
                return super(BoundField,self).css_classes(getattr(self.field,"css_classes"))
        else:
            return super(BoundField,self).css_classes(extra_classes)

    @property
    def is_display(self):
        return isinstance(self.field.widget,widgets.DisplayMixin)

    @property
    def is_hidden(self):
        return isinstance(self.field.widget,widgets.Hidden) and not self.field.widget.display_widget


    @property
    def initial(self):
        if self.is_display and hasattr(self.field.widget,"prepare_initial_data"):
            return self.field.widget.prepare_initial_data(self.form,self.name)
        data = super(BoundField,self).initial

        #print("{}: {} = {}".format("view" if self.is_display else "edit",self.name ,data))
        if not self.is_display and isinstance(data,models.Model):
            return data.pk
        else:
            return data

    @property
    def auto_id(self):
        if self.is_display:
            return ""
        else:
            html_id = super(BoundField,self).auto_id
            if "." in html_id:
                return html_id.replace(".","_")
            else:
                return html_id

    def html(self,template=None,method="as_widget"):
        if hasattr(self.field,"css_classes"):
            attrs = " class=\"{}\"".format(" ".join(self.field.css_classes))
        else:
            attrs = ""

        if template:
            return mark_safe(template.format(attrs=attrs,widget=getattr(self,method)()))
        else:
            return mark_safe(getattr(self,method)())

    def value(self):
        """
        Returns the value for this BoundField, using the initial value if
        the form is not bound or the data otherwise.
        """
        if not self.form.is_bound or isinstance(self.field.widget,widgets.DisplayWidget) or self.field.widget.attrs.get("disabled"):
            data = self.initial
        else:
            data = self.field.bound_data(
                self.data, self.form.initial.get(self.name, self.field.initial)
            )
        if isinstance(data,models.Model) and self.is_display:
            return data
        else:
            return self.field.prepare_value(data)

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        """
        Renders the field by rendering the passed widget, adding any HTML
        attributes passed as attrs.  If no widget is specified, then the
        field's default widget will be used.
        """
        if self.is_hidden:
            attrs = {'style':'display:none'}

        html = super(BoundField,self).as_widget(widget,attrs,only_initial)
        if not self.is_display and self.name in self.form.errors:
            html =  "<div class=\"error\">{}<p class=\"text-error\"><i class=\"icon-warning-sign\"></i> {}</p></div>".format(html,"<br>".join(self.form.errors[self.name]))
            pass
        return html

@html_safe
class CompoundBoundField(BoundField):
    """
    The boundfield for compound field
    """
    def __init__(self, form, field, name):
        super(CompoundBoundField,self).__init__(form,field,name)
        self.related_fields = [self.form[name] for name in field.related_field_names]

    def __str__(self):
        """Renders this field as an HTML widget."""
        if self.field.show_hidden_initial:
            return self.as_widget() + self.as_hidden(only_initial=True)
        return self.as_widget()

    def __iter__(self):
        """
        Yields rendered strings that comprise all widgets in this BoundField.

        This really is only useful for RadioSelect widgets, so that you can
        iterate over individual radio buttons in a template.
        """
        id_ = self.field.widget.attrs.get('id') or self.auto_id
        attrs = {'id': id_} if id_ else {}
        attrs = self.build_widget_attrs(attrs)
        for subwidget in self.field.widget.subwidgets(self.html_name, self.value(), attrs):
            yield subwidget

    def __len__(self):
        return len(list(self.__iter__()))

    def __getitem__(self, idx):
        # Prevent unnecessary reevaluation when accessing BoundField's attrs
        # from templates.
        if not isinstance(idx, six.integer_types + (slice,)):
            raise TypeError
        return list(self.__iter__())[idx]

    def get_field(self,field_name):
        return self.form[field_name]

    def get_fieldvalue(self,field_name):
        return self.form[field_name].value()

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        """
        Renders the field by rendering the passed widget, adding any HTML
        attributes passed as attrs.  If no widget is specified, then the
        field's default widget will be used.
        """
        #if self.name == "last_season_unknown":
        #    import ipdb;ipdb.set_trace()
        html_layout,field_names,include_primary_field = self.field.get_layout(self)
        if include_primary_field:
            html = super(CompoundBoundField,self).as_widget(widget,attrs,only_initial)
            if field_names:
                arguments = [f.as_widget(only_initial=only_initial) for f in self.related_fields if f.name in field_names]
                arguments.append(self.auto_id)
                return safestring.SafeText(html_layout.format(html,*arguments))
            elif html_layout:
                return safestring.SafeText(html_layout.format(html,self.auto_id))
            else:
                return html
        elif field_names:
                arguments = [f.as_widget(only_initial=only_initial) for f in self.related_fields if f.name in field_names]
                return safestring.SafeText(html_layout.format(*arguments))
        elif html_layout:
            return safestring.SafeText(html_layout)
        else:
            return ""

    def as_text(self, attrs=None, **kwargs):
        """
        Returns a string of HTML for representing this as an <input type="text">.
        """
        raise Exception("Not supported")

    def as_textarea(self, attrs=None, **kwargs):
        "Returns a string of HTML for representing this as a <textarea>."
        raise Exception("Not supported")

    def as_hidden(self, attrs=None, **kwargs):
        """
        Returns a string of HTML for representing this as an <input type="hidden">.
        """
        html = super(CompoundBoundField,self).as_widget(self.field.hidden_widget(), attrs, **kwargs)
        return self.field.hidden_layout.format(html,*[f.as_widget(f.field.hidden_widget(),None,**kwargs) for f in self.related_fields])

class ListBoundFieldMixin(object):
    def __init__(self, form, field, name):
        super(ListBoundFieldMixin,self).__init__(form,field,name)
        self.sortable = name in self.form._meta.sortable_fields if self.form._meta.sortable_fields else False

    @property
    def sorting_status(self):
        if not self.sortable:
            return None
        elif not self.form.sorting_status :
            return "sortable"
        elif self.name == self.form.sorting_status[0]:
            return "asc" if self.form.sorting_status[1] else "desc"
        else:
            return "sortable"

    @property
    def sorting_html_class(self):
        """
        return sort html class if have; otherwise return ""
        """
        if not self.sortable:
            return ""
        elif not self.form.sorting_status :
            return getattr(self.form._meta,"sorting_html_class")
        elif self.name == self.form.sorting_status[0]:
            return getattr(self.form._meta,"asc_sorting_html_class" if self.form.sorting_status[1] else "desc_sorting_html_class")
        else:
            return getattr(self.form._meta,"sorting_html_class")

    def html_toggle(self,template):
        label = (conditional_escape(self.label) or '') if self.label else ''

        if self.form._meta.default_toggled_fields and self.name in self.form._meta.default_toggled_fields:
            activeclass = " btn-info"
        else:
            activeclass = ""

        return mark_safe(template.format(name=self.name,label=label,activeclass=activeclass))


    def html_header(self,template):
        label = (conditional_escape(self.label) or '') if self.label else ''

        if self.is_hidden:
            if self.form._meta.widths and self.form_field_name in self.form._meta.widths:
                attrs = ""
            else:
                attrs = " style='display:none'"
        elif not self.sortable:
            if hasattr(self.field,"css_classes"):
                attrs = " class=\"{}\"".format(" ".join(self.field.css_classes))
            else:
                attrs = ""
        else:
            sorting_status = self.sorting_status
            sorting_class = self.sorting_html_class
            if hasattr(self.field,"css_classes"):
                attrs = " onclick=\"document.location='{}'\" class=\"{} {}\"".format(self.form.querystring(ordering="{}{}".format("-" if sorting_status == 'asc' else '',self.name)),sorting_class," ".join(self.field.css_classes))
            else:
                attrs = " onclick=\"document.location='{}'\" class=\"{}\"".format(self.form.querystring(ordering="{}{}".format("-" if sorting_status == 'asc' else '',self.name)),sorting_class)

        if self.form._meta.widths and self.form_field_name in self.form._meta.widths:
            attrs = "{} style='width:{};'".format(attrs,self.form._meta.widths[self.form_field_name])

        return mark_safe(template.format(label=label,attrs=attrs))

    def html(self,template):
        if self.is_hidden:
            attrs = " style='display:none'"
        elif hasattr(self.field,"css_classes"):
            attrs = " class=\"{}\"".format(" ".join(self.field.css_classes))
        else:
            attrs = ""

        return mark_safe(template.format(attrs=attrs,widget=self.as_widget()))

        
class ListBoundField(ListBoundFieldMixin,BoundField):
    pass

class CompoundListBoundField(ListBoundFieldMixin,CompoundBoundField):
    pass


class BoundFormField(BoundField):
    def __init__(self,*args,**kwargs):
        super(BoundFormField,self).__init__(*args,**kwargs)
        self._bound_fields_cache = {}
        if self.form.is_bound and not self.field.is_display:
            raise NotImplementedError
        else:
            self.innerform = self.field.form_class(instance=self.value(),prefix=self.name)

    @property
    def initial(self):
        return self.form.initial.get(self.name, self.field.get_initial())

    def html(self,template=None,method="as_widget"):
        raise NotImplementedError

    @property
    def is_bound(self):
        return self.form.is_bound and not self.field.is_display

    def value(self):
        """
        Returns the value for this BoundField, using the initial value if
        the form is not bound or the data otherwise.
        """
        if self.form.is_bound and not self.field.is_display:
            raise NotImplementedError
        else:
            return self.form.initial.get(self.name, self.field.get_initial())

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        raise NotImplementedError

    def __getitem__(self, name):
        """Return a BoundField with the given name."""
        try:
            field = self.field.form_class.base_fields[name]
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
                self._bound_fields_cache[name] = CompoundBoundField(self.innerform,field,name)
            else:
                self._bound_fields_cache[name] = BoundField(self.innerform,field,name)
        return self._bound_fields_cache[name]
    
class BoundFormSetField(BoundField):
    def __init__(self,*args,**kwargs):
        super(BoundFormSetField,self).__init__(*args,**kwargs)
        self.formset = self.field.formset_class(data=self.form.data if self.form.is_bound else None,instance_list=self.initial,prefix=self.name,parent_instance=self.form.instance)

    @property
    def initial(self):
        return self.form.initial.get(self.name, self.field.get_initial())

    def html(self,template=None,method="as_widget"):
        raise NotImplementedError

    @property
    def is_bound(self):
        return self.form.is_bound and not self.field.is_display

    def clean_field(self):
        if self.formset.is_valid():
            return [form.cleaned_data for form in self.formset]
        else:
           raise ValidationError("") #error placeholder, but not display in page

    def post_clean(self):
        for form in self.formset:
            form._post_clean()

    def clean(self):
        for form in self.formset:
            form._clean_form()

        self.formset.clean()

    def save(self):
        for form in self.formset:
            if form.can_delete:
                if form.instance.pk:
                    form.instance.delete()
            else:
                form.save()

    def as_widget(self, widget=None, attrs=None, only_initial=False):
        return "{}{}".format(str(self.formset.management_form),self.field.template.render({"formset":self.formset,"errors":self.form.errors.get(self.name)}))

    def __iter__(self):
        return self.formset


    
