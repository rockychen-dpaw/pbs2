from collections import OrderedDict

from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import html_safe
from django.forms.utils import ErrorList
from django.db import transaction
from django.utils import six
from django import forms
from django.db import models
from django.template.defaultfilters import safe
from django.utils import safestring

from . import widgets
from . import fields
from .boundfield import BoundField,CompoundBoundField

from .utils import FieldClassConfigDict,FieldWidgetConfigDict,SubpropertyEnabledDict,ChainDict
from ..models import DictMixin

class BaseModelFormMetaclass(forms.models.ModelFormMetaclass):
    """
    Extend django's ModelFormMetaclass to support the following features
    1. Inheritance the meta properties from super class
    2. automatically populate 'update_fields' when saving a model instance
    3. new property 'field_classes_config' to config the field class for editing and view
    4. new property 'widgets_config' to config widget for editing and view
    5. new property 'other_fields' to support readonly model field and class property field
    6. new property 'editable_fields' to list all editable fields
    7. new property 'ordered_fields' to support sort fields
    8. new property 'extra_update_fields' to add extra update fields to 'update_fields' whensaving a model instance
    9. new property 'purpose' to indicate the purpose of this form

    Add the following properties into _meta property of model instance
    1. subproperty_enabled: True if some form field is created for subproperty of a model field or model property
    2. update_db_fields: possible db fields which can be updated through the form instance
    3. update_model_properties: possible model properties or subproperties which can be updated through the form instance
    4. editable_fields: the editable form fields
    """
 
    @staticmethod
    def meta_item_from_base(bases,name):
        for b in bases:
            if hasattr(b, 'Meta') and hasattr(b.Meta, name):
                return getattr(b.Meta,name)
        return None

    def __new__(mcs, name, bases, attrs):
        base_formfield_callback = None
        #inheritence some configuration from super class
        if 'Meta' in attrs :
            if not hasattr(attrs['Meta'],'exclude') and not hasattr(attrs["Meta"],"fields"):
                config = BaseModelFormMetaclass.meta_item_from_base(bases,'exclude')
                if config:
                    setattr(attrs["Meta"],"exclude",config)
                config = BaseModelFormMetaclass.meta_item_from_base(bases,'fields')
                if config:
                    setattr(attrs["Meta"],"fields",config)

            for item in ("other_fields","extra_update_fields","ordered_fields",'purpose'):
                if not hasattr(attrs['Meta'],item):
                    config = BaseModelFormMetaclass.meta_item_from_base(bases,item)
                    if config:
                        setattr(attrs["Meta"],item,config)

            for item in ("editable_fields",):
                if not hasattr(attrs['Meta'],item):
                    config = BaseModelFormMetaclass.meta_item_from_base(bases,item)
                    if config:
                        setattr(attrs["Meta"],item,config)
                    else:
                        setattr(attrs["Meta"],item,None)


            for item in ("field_classes_config","widgets_config"):
                config = BaseModelFormMetaclass.meta_item_from_base(bases,item)
                if not hasattr(attrs['Meta'],item):
                    if config:
                        setattr(attrs["Meta"],item,config)
                    else:
                        setattr(attrs["Meta"],item,{})
                elif config:
                    config = dict(config)
                    config.update(getattr(attrs['Meta'],item))
                    setattr(attrs['Meta'],item, config)

            for item in ("formfield_callback",):
                if not hasattr(attrs['Meta'],item):
                    config = BaseModelFormMetaclass.meta_item_from_base(bases,item)
                    if config:
                        if hasattr(config,"__func__"):
                            setattr(attrs["Meta"],item,staticmethod(config.__func__))
                        else:
                            setattr(attrs["Meta"],item,staticmethod(config))

            for item in ("is_dbfield",):
                if not hasattr(attrs['Meta'],item):
                    config = BaseModelFormMetaclass.meta_item_from_base(bases,item)
                    if config:
                        if hasattr(config,"__func__"):
                            setattr(attrs["Meta"],item,classmethod(config.__func__))
                        else:
                            setattr(attrs["Meta"],item,classmethod(config))

            for item in ("labels",):
                config = BaseModelFormMetaclass.meta_item_from_base(bases,item)
                if config:
                    if hasattr(attrs['Meta'],item):
                        getattr(attrs['Meta'],item).update(config)
                    
                    else:
                        setattr(attrs['Meta'],item,config)


            setattr(attrs['Meta'],"field_classes",FieldClassConfigDict(attrs['Meta'],attrs['Meta'].field_classes_config))
            setattr(attrs['Meta'],"widgets",FieldWidgetConfigDict(attrs['Meta'],attrs['Meta'].widgets_config))

        new_class = super(BaseModelFormMetaclass, mcs).__new__(mcs, name, bases, attrs)
        meta = getattr(new_class,"Meta") if hasattr(new_class,"Meta") else None
        opts = getattr(new_class,"_meta") if hasattr(new_class,"_meta") else None
        if not opts or not meta or not hasattr(meta,"model"):
            return new_class


        for item in ("other_fields","extra_update_fields","ordered_fields","field_classes_config","widgets_config","editable_fields","purpose"):
            if hasattr(meta,item) :
                setattr(opts,item,getattr(meta,item))
            else:
                setattr(opts,item,None)

        formfield_callback = meta.formfield_callback if meta and hasattr(meta,"formfield_callback") else None

        model = opts.model
        model_field = None
        field_list = []
        kwargs = {}
        db_field = True
        property_name = None
        subproperty_enabled = False
        
        for field_name in opts.other_fields or []:
            if "." in field_name:
                property_name = field_name.split(".",1)[0]
                subproperty_enabled = True
            else:
                property_name = field_name
            try:
                if field_name != property_name:
                    raise Exception("Not a model field")
                model_field = model._meta.get_field(field_name)
                db_field = True
            except:
                #not a model field, check whether it is a property 
                if hasattr(model,property_name) and isinstance(getattr(model,property_name),property):
                    #field is a property
                    if field_name == property_name:
                        model_field = getattr(model,property_name)
                    else:
                        #a sub property of a model property
                        model_field = None
                    db_field = False
                else:
                    raise Exception("Unknown field {} ".format(field_name))

            kwargs.clear()
            if hasattr(opts,"field_classes")  and opts.field_classes and field_name in opts.field_classes and isinstance(opts.field_classes[field_name],forms.Field):
                #already configure a form field instance, use it directly
                form_field = opts.field_classes[field_name]
                field_list.append((field_name, formfield))
                continue

            try:
                kwargs['widget'] = opts.widgets[field_name]
            except KeyError as ex:
                if not db_field:
                    raise Exception("Please configure widget for property '{}' in 'widgets' option".format(field_name))

            if opts.localized_fields == forms.models.ALL_FIELDS or (opts.localized_fields and field_name in opts.localized_fields):
                kwargs['localize'] = True

            if opts.labels and field_name in opts.labels:
                kwargs['label'] = safe(opts.labels[field_name])
            elif not db_field:
                kwargs['label'] = safe(field_name)

            if opts.help_texts and field_name in opts.help_texts:
                kwargs['help_text'] = opts.help_texts[field_name]

            if opts.error_messages and field_name in opts.error_messages:
                kwargs['error_messages'] = opts.error_messages[field_name]

            if not db_field:
                kwargs['required'] = False

            try:
                kwargs['form_class'] = opts.field_classes[field_name]
            except KeyError as ex:
                if not db_field :
                    raise Exception("Please cofigure form field for property '{}' in 'field_classes' option".format(field_name))

            if formfield_callback is None:
                if db_field:
                    formfield = model_field.formfield(**kwargs)
                else:
                    formfield = kwargs.pop('form_class')(**kwargs)
            elif not callable(formfield_callback):
                raise TypeError('formfield_callback must be a function or callable')
            else:
                formfield = formfield_callback(model_field, **kwargs)

            field_list.append((field_name, formfield))

        setattr(opts,'subproperty_enabled',subproperty_enabled)

        if field_list:
            field_list = OrderedDict(field_list)
            new_class.base_fields.update(field_list)

        if hasattr(new_class,"all_base_fields"):
            new_class.all_base_fields.update(new_class.base_fields)
        else:
            new_class.all_base_fields = new_class.base_fields

        if opts.ordered_fields:
            new_class.base_fields = OrderedDict()
            for field in opts.ordered_fields:
                if field in new_class.all_base_fields:
                    new_class.base_fields[field] = new_class.all_base_fields[field]

        update_db_fields = list(getattr(opts,"extra_update_fields") or [])
        update_model_properties = []

        for name,field in new_class.base_fields.items():
            if isinstance(field.widget,widgets.DisplayMixin):
                continue
            if "." in name:
                #not a model field
                update_model_properties.append(name)
                continue
            try:
                model._meta.get_field(name)
                update_db_fields.append(name)
            except:
                #not a model field
                update_model_properties.append(name)
                continue

        setattr(opts,'update_db_fields',update_db_fields)
        setattr(opts,'update_model_properties',update_model_properties)
        
        return new_class

class ModelForm(six.with_metaclass(BaseModelFormMetaclass, forms.models.BaseModelForm)):
    """
    This class only support model class which extends DictMixin

    The following features are supported.
    1. is_editable: to check whether a field is editable or not.
    2. save_properties: called right after save() method in the same transaction if update_model_properties is not emtpy.
    3. set the value of model properties or model subproperties from form instance before seting the value of model fields

    """
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None, use_required_attribute=None,
                 renderer=None):
        """
        The reason to totally override initial method of BaseModelForm is using ChainDict to replace model_to_dict method call
        """
        opts = self._meta
        if opts.model is None:
            raise ValueError('ModelForm has no model class specified.')
        if instance is None:
            # if we didn't get an instance, instantiate a new one
            self.instance = opts.model()
        else:
            self.instance = instance

        if self.instance:
            if not isinstance(self.instance,DictMixin) :
                raise "{}.{} does not extend from DictMixin".format(self.instance.__class__.__module__,self.instance.__class__.__name__)

        if instance and initial:
            initial = ChainDict([initial,instance])
        elif instance:
            initial = instance
        elif initial:
            initial = initial
        else:
            initial = {}

        if self._meta.subproperty_enabled:
            initial = SubpropertyEnabledDict(initial)

        # self._validate_unique will be set to True by BaseModelForm.clean().
        # It is False by default so overriding self.clean() and failing to call
        # super will stop validate_unique from being called.
        self._validate_unique = False
        forms.forms.BaseForm.__init__(self,
            data, files, auto_id, prefix, initial, error_class,
            label_suffix, empty_permitted, use_required_attribute=use_required_attribute,
            renderer=renderer,
        )
        for formfield in self.fields.values():
            forms.models.apply_limit_choices_to_to_formfield(formfield)

    def is_editable(self,name):
        return self._meta.editable_fields is None or name in self._meta.editable_fields

    def _post_clean(self):
        #save the value of model properties
        if self._meta.update_model_properties:
            for name in self._meta.update_model_properties:
                if name not in self.cleaned_data:
                    continue
                if "." in name:
                    props = name.split(".")
                    result = getattr(self.instance,props[0])
                    for prop in props[1:-1]:
                        try:
                            result = result[prop]
                        except KeyError as ex:
                            result[prop] = {}
                            result = result[prop]
                    result[props[-1]] = self.cleaned_data[name]
                else:
                    setattr(self.instance,name,self.cleaned_data[name])
        super(ModelForm,self)._post_clean()

    def save(self, commit=True):
        """
        Save this form's self.instance object if commit=True. Otherwise, add
        a save_m2m() method to the form which can be called after the instance
        is saved manually at a later time. Return the model instance.
        """
        update_properties = self._meta.update_model_properties and hasattr(self.instance,"save_properties") and callable(getattr(self.instance, "save_properties"))

        if self.instance.pk and hasattr(self._meta,"update_db_fields") and self._meta.editable_fields:
            if self.errors:
                raise ValueError(
                    "The %s could not be %s because the data didn't validate." % (
                        self.instance._meta.object_name,
                        'created' if self.instance._state.adding else 'changed',
                    )
                )
            if commit:
                # If committing, save the instance and the m2m data immediately.
                with transaction.atomic():
                    self.instance.save(update_fields=self._meta.update_db_fields)
                    if update_properties:
                        self.instance.save_properties(update_fields=self._meta.update_model_properties)
                self._save_m2m()
            else:
                # If not committing, add a method to the form to allow deferred
                # saving of m2m data.
                self.save_m2m = self._save_m2m
        elif commit:
            with transaction.atomic():
                super(ModelForm,self).save(commit)
                if update_properties:
                    self.instance.save_properties(update_fields=self._meta.update_model_properties)

        else:
            super(ModelForm,self).save(commit)


        return self.instance

    def full_clean(self):
        if self._meta.editable_fields is None:
            super(ModelForm,self).full_clean()
            return

        opt_fields = self._meta.fields
        fields = self.fields
        try:
            self._meta.fields = self._meta.editable_fields
            self.editable_fields = self.editable_fields if hasattr(self,'editable_fields') else dict([(n,f) for n,f in self.fields.items() if n in self._meta.fields])
            self.fields = self.editable_fields
            super(ModelForm,self).full_clean()
        finally:
            self._meta.fields = opt_fields
            self.fields = fields

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
                self._bound_fields_cache[name] = CompoundBoundField(self,field,name)
            else:
                self._bound_fields_cache[name] = BoundField(self,field,name)
        return self._bound_fields_cache[name]
    
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


            

