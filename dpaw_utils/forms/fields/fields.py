import json

from django import forms

from dpaw_utils.utils import ConditionalChoice
from .. import widgets
from ..utils import hashvalue,JSONEncoder
from .coerces import *
from ..boundfield import (CompoundBoundField,)

class_id = 0
field_classes = {}

def hide_field(field):
    """
    Add some widget attributes to hide the field in html page
    """
    if field.widget.attrs:
        if field.widget.attrs.get("style"): 
            field.widget.attrs["style"]  = "{};{}".format(field.widget.attrs["style"],"display:none")
        else:
            field.widget.attrs["style"]  = "display:none"
        field.widget.attrs["disabled"]  = True
    else:
        field.widget.attrs = {"style":"display:none","disabled":True}

DIRECTION_CHOICES = (
    ("","---"),
    ("N","N"),
    ("NNE","NNE"),
    ("NE","NE"),
    ("ENE","ENE"),
    ("E","E"),
    ("ESE","ESE"),
    ("SE","SE"),
    ("SSE","SSE"),
    ("S","S"),
    ("SSW","SSW"),
    ("SW","SW"),
    ("WSW","WSW"),
    ("W","W"),
    ("WNW","WNW"),
    ("NW","NW"),
    ("NNW","NNW")
)
class NullDirectionField(forms.ChoiceField):
    def __init__(self,**kwargs):
        super(NullDirectionField,self).__init__(choices=DIRECTION_CHOICES,**kwargs)

class FieldParametersMixin(object):
    """
    A mixin to inject some parameters into field instance.
    """
    field_params = None

    def __init__(self,*args,**kwargs):
        if self.field_params:
            for k,v in self.field_params.items():
                kwargs[k] = v
        super(FieldParametersMixin,self).__init__(*args,**kwargs)

def OverrideFieldFactory(model,field_name,field_class=None,**kwargs):
    """
    A factory method to create a compoundfield class
    """
    global class_id

    kwargs = kwargs or {}
    field_class = field_class or model._meta.get_field(field_name).formfield().__class__
    class_key = hashvalue("OverrideField<{}.{}.{}.{}.{}.{}>".format(model.__module__,model.__name__,field_name,field_class.__module__,field_class.__name__,json.dumps(kwargs,cls=JSONEncoder)))
    if class_key not in field_classes:
        class_id += 1
        class_name = "{}_{}".format(field_class.__name__,class_id)
        kwargs.update({"field_name":field_name})
        field_classes[class_key] = type(class_name,(FieldParametersMixin,field_class),kwargs)
        #print("{}.{}={}".format(field_name,field_classes[class_key],field_classes[class_key].get_layout))
    return field_classes[class_key]

class AliasFieldMixin(object):
    field_name = None

def AliasFieldFactory(model,field_name,field_class=None,field_params=None):
    global class_id
    field_class = field_class or model._meta.get_field(field_name).formfield().__class__
    if field_params:
        class_key = hashvalue("AliasField<{}.{}{}{}{}>".format(model.__module__,model.__name__,field_name,field_class,json.dumps(field_params,cls=JSONEncoder)))
    else:
        class_key = hashvalue("AliasField<{}.{}{}{}>".format(model.__module__,model.__name__,field_name,field_class))

    if class_key not in field_classes:
        class_id += 1
        class_name = "{}_{}".format(field_class.__name__,class_id)
        if field_params:
            field_classes[class_key] = type(class_name,(FieldParametersMixin,AliasFieldMixin,field_class),{"field_name":field_name,"field_params":field_params})
        else:
            field_classes[class_key] = type(class_name,(AliasFieldMixin,field_class),{"field_name":field_name})
    return field_classes[class_key]

class CompoundField(AliasFieldMixin,FieldParametersMixin):
    """
    A base class of compund field which consists of multiple form fields
    """
    related_field_names = []
    field_mixin = None
    hidden_layout = None
    editmode = None

    def  get_layout(self,f):
        if self.editmode == True:
            return self._edit_layout(f)
        elif isinstance(self.widget,widgets.DisplayWidget):
            return self._view_layout(f)
        else:
            return self._edit_layout(f)

    def _view_layout(self,f):
        raise Exception("Not implemented")

    def _edit_layout(self,f):
        raise Exception("Not implemented")

def CompoundFieldFactory(compoundfield_class,model,field_name,related_field_names=None,field_class=None,**kwargs):
    """
    A factory method to create a compoundfield class
    """
    global class_id

    kwargs = kwargs or {}
    if not related_field_names:
        related_field_names = compoundfield_class.related_field_names
    if hasattr(compoundfield_class,"init_kwargs") and callable(compoundfield_class.init_kwargs):
        kwargs = compoundfield_class.init_kwargs(model,field_name,related_field_names,kwargs)

    hidden_layout="{}" * (len(related_field_names) + 1)
    field_class = field_class or model._meta.get_field(field_name).formfield().__class__
    class_key = hashvalue("CompoundField<{}.{}.{}.{}.{}.{}.{}.{}>".format(compoundfield_class.__name__,model.__module__,model.__name__,field_name,field_class.__module__,field_class.__name__,json.dumps(related_field_names),json.dumps(kwargs,cls=JSONEncoder)))
    if class_key not in field_classes:
        class_id += 1
        class_name = "{}_{}".format(field_class.__name__,class_id)
        kwargs.update({"field_name":field_name,"related_field_names":related_field_names,"hidden_layout":hidden_layout})
        field_classes[class_key] = type(class_name,(compoundfield_class,field_class),kwargs)
        #print("{}.{}={}".format(field_name,field_classes[class_key],field_classes[class_key].get_layout))
    return field_classes[class_key]

def SwitchFieldFactory(model,field_name,related_field_names,field_class=None,**kwargs):
    return CompoundFieldFactory(SwitchField,model,field_name,related_field_names,field_class,**kwargs)

def OtherOptionFieldFactory(model,field_name,related_field_names,field_class=None,**kwargs):
    return CompoundFieldFactory(OtherOptionField,model,field_name,related_field_names,field_class,**kwargs)

def MultipleFieldFactory(model,field_name,related_field_names,field_class=None,**kwargs):
    return CompoundFieldFactory(MultipleField,model,field_name,related_field_names,field_class,**kwargs)

def ConditionalMultipleFieldFactory(model,field_name,related_field_names,field_class=None,**kwargs):
    return CompoundFieldFactory(ConditionalMultipleField,model,field_name,related_field_names,field_class,**kwargs)

class ChoiceFieldMixin(object):
    def __init__(self,*args,**kwargs):
        kwargs["choices"] = self.CHOICES
        for key in ("min_value","max_value","max_length","limit_choices_to","to_field_name","queryset"):
            if key in kwargs:
                del kwargs[key]
        super(ChoiceFieldMixin,self).__init__(*args,**kwargs)

def ChoiceFieldFactory(choices,choice_class=forms.TypedChoiceField,field_params=None,type_name=None):
    global class_id
    if type_name:
        class_key = hashvalue("ChoiceField<{}.{}{}{}>".format(choice_class.__module__,choice_class.__name__,type_name,json.dumps(field_params,cls=JSONEncoder)))
    else:
        class_key = hashvalue("ChoiceField<{}.{}{}{}>".format(choice_class.__module__,choice_class.__name__,json.dumps(choices),json.dumps(field_params,cls=JSONEncoder)))
    if class_key not in field_classes:
        class_id += 1
        class_name = "{}_{}".format(choice_class.__name__,class_id)
        field_classes[class_key] = type(class_name,(FieldParametersMixin,ChoiceFieldMixin,choice_class),{"CHOICES":choices,"field_params":field_params})
    return field_classes[class_key]


NOT_NONE=1
HAS_DATA=2
ALWAYS=3
DATA_MAP=4
class SwitchField(CompoundField):
    """
    suitable for compound fields which include a boolean primary field and one or more related field or a html section
    normally, when the primary feild is false, all related field will be disabled; when primary field is true, all related field will be enabled

    policy: the policy to view the related field when primary field if false.
    reverse: if reverse is true; the behaviour will be reversed; that means: all related field will be disabled when the primary field is true
    on_layout: the view layout when the primary field is true
    off_layout: the view layout when the primary field is false
    edit_layout: the edit layout
    """
    policy = HAS_DATA
    reverse = False
    on_layout = None
    off_layout = None
    edit_layout = None
    true_value = 'True'

    @classmethod
    def init_kwargs(cls,model,field_name,related_field_names,kwargs):
        if not kwargs.get("on_layout"):
            kwargs["on_layout"] = u"{{}}{}".format("<br>{}" * len(related_field_names))

        if not kwargs.get("off_layout"):
            kwargs["off_layout"] = None

        if not kwargs.get("edit_layout"):
            kwargs["edit_layout"] = u"{{0}}<div id='id_{}_body'>{{1}}{}</div>".format(
                "{{{}}}".format(len(related_field_names) + 1),
                "".join(["<br>{{{}}}".format(i) for i in range(2,len(related_field_names) + 1)])
            )

        kwargs["true_value"] = (str(kwargs['true_value']) if kwargs['true_value'] is not None else "" ) if "true_value" in kwargs else 'True'

        return kwargs

    def _view_layout(self,f):
        """
        return a tuple(layout,enable related field list) for view
        """
        val1 = f.value()
        val1_str = str(val1) if val1 is not None else ""
        if (not self.reverse and val1_str == self.true_value) or (self.reverse and not val1_str == self.true_value):
            if self.policy == ALWAYS:
                return (self.off_layout if self.reverse else self.on_layout,f.field.related_field_names,True)
            else:
                val2 = f.related_fields[0].value()
                if self.policy == NOT_NONE and val2 is not None:
                    return (self.off_layout if self.reverse else self.on_layout,f.field.related_field_names,True)
                elif self.policy == HAS_DATA and val2:
                    return (self.off_layout if self.reverse else self.on_layout,f.field.related_field_names,True)
                
        return (self.on_layout if self.reverse else self.off_layout,None,True)

        
    def _edit_layout(self,f):
        """
        return a tuple(layout,enable related field list) for edit
        """
        val1 = f.value()
        val1_str = str(val1) if val1 is not None else ""
            
        f.field.widget.attrs = f.field.widget.attrs or {}
        show_fields = "$('#id_{}_body').show();{}".format(f.auto_id,";".join(["$('#{0}').prop('disabled',false)".format(field.auto_id) for field in f.related_fields]))
        hide_fields = "$('#id_{}_body').hide();{}".format(f.auto_id,";".join(["$('#{0}').prop('disabled',true)".format(field.auto_id) for field in f.related_fields]))

        condition = None

        if isinstance(f.field.widget,forms.widgets.RadioSelect):
            condition ="document.getElementById('{0}').value === '{1}'".format(f.auto_id,str(self.true_value))
            f.field.widget.attrs["onclick"]="show_{}()".format(f.auto_id)
        elif isinstance(f.field.widget,forms.widgets.CheckboxInput):
            condition ="document.getElementById('{0}').checked".format(f.auto_id)
            f.field.widget.attrs["onclick"]="show_{}()".format(f.auto_id)
        elif isinstance(f.field.widget,forms.widgets.Select):
            condition ="document.getElementById('{0}').value === '{1}'".format(f.auto_id,str(self.true_value))
            f.field.widget.attrs["onchange"]="show_{}()".format(f.auto_id)
        else:
            raise Exception("Not implemented")

        js_script ="""
            <script type="text/javascript">
                function show_{0}() {{{{
                    if ({1}) {{{{
                      {2}
                    }}}} else {{{{
                        {3}
                    }}}}
                }}}}
                $(document).ready(show_{0})
            </script>
        """.format(f.auto_id,condition,hide_fields if self.reverse else show_fields,show_fields if self.reverse else hide_fields)

        return (u"{}{}".format(self.edit_layout,js_script),f.field.related_field_names,True)
    
class OtherOptionField(CompoundField):
    """
    suitable for compound fields which include a choice primary field with other options and one or more related field

    other_layout: is used when other option is chosen
    layout: is used when other option is not chosen
    edit_layout: is used for editing
    """
    policy = HAS_DATA
    other_layout = None
    layout = None
    edit_layout = None
    other_option = None

    @classmethod
    def init_kwargs(cls,model,field_name,related_field_names,kwargs):
        if not kwargs.get("other_option"):
            raise Exception("Missing 'other_option' keyword parameter")

        if not kwargs.get("other_layout"):
            kwargs["other_layout"] = u"{{}}{}".format("<br>{}" * len(related_field_names))

        if not kwargs.get("layout"):
            kwargs["layout"] = None

        if not kwargs.get("edit_layout"):
            kwargs["edit_layout"] = u"{{0}}<div id='id_{}_body'>{{1}}{}</div>".format(
                "{{{}}}".format(len(related_field_names) + 1),
                "".join(["<br>{{{}}}".format(i) for i in range(2,len(related_field_names) + 1)])
            )

        return kwargs

    def _view_layout(self,f):
        val1 = f.value()
        if val1 == self.other_option:
            val2 = f.related_fields[0].value()
            if self.policy == ALWAYS:
                return (self.other_layout,f.field.related_field_names,True)
            elif self.policy == NOT_NONE and val2 is not None:
                return (self.other_layout,f.field.related_field_names,True)
            elif self.policy == HAS_DATA and val2:
                return (self.other_layout,f.field.related_field_names,True)
            elif self.policy == DATA_MAP and val2 in self.other_layout:
                return (self.other_layout[val2],f.field.related_field_names,True)
                
        return (self.layout,None,True)

    def _edit_layout(self,f):
        """
        return a tuple(layout,enable related field list) for edit
        """
        val1 = f.value()
        if isinstance(val1,basestring):
            val1 = int(val1) if val1 else None
        #if f.name == "field_officer":
        #    import ipdb;ipdb.set_trace()
        other_value = self.other_option.id if hasattr(self.other_option,"id") else self.other_option

        f.field.widget.attrs = f.field.widget.attrs or {}
        show_fields = "$('#id_{}_body').show();{}".format(f.auto_id,";".join(["$('#{0}').prop('disabled',false)".format(field.auto_id) for field in f.related_fields]))
        hide_fields = "$('#id_{}_body').hide();{}".format(f.auto_id,";".join(["$('#{0}').prop('disabled',true)".format(field.auto_id) for field in f.related_fields]))

        if isinstance(f.field.widget,forms.widgets.RadioSelect):
            f.field.widget.attrs["onclick"]="""
                if (this.value === '{0}') {{
                    {1}
                }} else {{
                    {2}
                }}
            """.format(str(other_value),show_fields,hide_fields)
        elif isinstance(f.field.widget,forms.widgets.Select):
            f.field.widget.attrs["onchange"]="""
                if (this.value === '{0}') {{
                    {1}
                }} else {{
                    {2}
                }}
            """.format(str(other_value),show_fields,hide_fields)
        else:
            raise Exception("Not  implemented")

        if val1 != other_value:
            return (u"{}<script type='text/javascript'>{}</script>".format(self.edit_layout,hide_fields),f.field.related_field_names,True)
        else:
            return (self.edit_layout,f.field.related_field_names,True)
        
    
class MultipleField(CompoundField):
    """
    just combine multiple fields

    layout: is used when other option is not chosen
    """
    layout = None

    @classmethod
    def init_kwargs(cls,model,field_name,related_field_names,kwargs):
        if not kwargs.get("layout"):
            kwargs["layout"] = u"{{0}} {}".format("".join(["<br>{{{}}}".format(i) for i in range(1,len(related_field_names) + 1)]))

        return kwargs

    def _view_layout(self,f):
        return (self.layout,f.field.related_field_names,True)

    def _edit_layout(self,f):
        """
        return a tuple(layout,enable related field list) for edit
        """
        return (self.layout,f.field.related_field_names,True)
        
class ConditionalMultipleField(CompoundField):
    """
    view/edit multiple fields with condition

    """
    view_layouts = None
    edit_layouts = None

    @classmethod
    def init_kwargs(cls,model,field_name,related_field_names,kwargs):
        if kwargs.get("view_layouts"):
            kwargs["view_layouts"] = ConditionalChoice(kwargs["view_layouts"])
        else:
            kwargs["view_layouts"] = ConditionalChoice([(lambda f:True,u"{{0}} {}".format("".join(["<br>{{{}}}".format(i) for i in range(1,len(related_field_names) + 1)])))])

        if kwargs.get("edit_layouts"):
            kwargs["edit_layouts"] = ConditionalChoice(kwargs["edit_layouts"])
        else:
            kwargs["edit_layouts"] = ConditionalChoice([(lambda f:True,u"{{0}} {}".format("".join(["<br>{{{}}}".format(i) for i in range(1,len(related_field_names) + 1)])))])

        return kwargs

    def _view_layout(self,f):
        return self.view_layouts[f]

    def _edit_layout(self,f):
        return self.edit_layouts[f]
        
    
BooleanChoiceField = ChoiceFieldFactory([
    (True,"Yes"),
    (False,"No")
],field_params={"coerce":coerce_TrueFalse,'empty_value':None},type_name="BooleanChoiceField")

BooleanChoiceFilter = ChoiceFieldFactory([
    (True,"Yes"),
    (False,"No")
    ],choice_class=forms.TypedMultipleChoiceField ,field_params={"coerce":coerce_TrueFalse,'empty_value':None,'required':False},type_name="BooleanChoiceFilter")

NullBooleanChoiceFilter = ChoiceFieldFactory([
    ('',"Unknown"),
    (True,"Yes"),
    (False,"No")
    ],choice_class=forms.TypedMultipleChoiceField ,field_params={"coerce":coerce_TrueFalse,'empty_value':None,'required':False},type_name="NullBooleanChoiceFilter")


