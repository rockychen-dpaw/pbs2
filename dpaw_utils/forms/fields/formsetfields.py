
from django import forms
from django.template import engines

from .. import widgets
from ..utils import hashvalue
from .fields import (class_id,field_classes)

django_engine = engines['django']
class FormSetField(forms.Field):
    _formset_class = None
    _template = None
    def __init__(self, *args,**kwargs):
        kwargs["widget"] = kwargs["widget"] or TextDisplay()
        kwargs["initial"] = None
        initial = None
        super(FormSetField,self).__init__(*args,**kwargs)

        self._is_display = True
        for f in self._formset_class.form.base_fields.values():
            if not isinstance(f.widget,widgets.DisplayMixin):
                self._is_display = False
                break


    @property
    def template(self):
        return self._template

    @property
    def formset_class(self):
        return self._formset_class

    @property
    def model(self):
        return self._formset_class._meta.model

    @property
    def is_display(self):
        return self._is_display

    def get_initial(self):
        """
        guarantee a non-none value will be returned
        """
        if not self.initial:
            self.initial = self.formset_class.form._meta.model()
        return self.initial

def FormSetFieldFactory(formset_class,template):
    global class_id

    class_key = hashvalue("FormSetField<{}.{}>".format(formset_class.__module__,formset_class.__name__))
    if class_key not in field_classes:
        class_id += 1
        class_name = "FormSetField_{}".format(class_id)
        field_classes[class_key] = type(class_name,(FormSetField,),{"_formset_class":formset_class,"_template":django_engine.from_string(template)})
    return field_classes[class_key]


