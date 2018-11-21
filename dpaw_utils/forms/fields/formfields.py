
from django import forms

from ..forms import ModelForm
from ..boundfield import (BoundField,CompoundBoundField)
from ..widgets import (TextDisplay,DisplayMixin)
from ..utils import hashvalue
from .fields import (class_id,field_classes)

class FormField(forms.Field):
    _form_class = None
    def __init__(self, *args,**kwargs):
        kwargs["widget"] = kwargs["widget"] or TextDisplay()
        kwargs["initial"] = None
        initial = None
        super(FormField,self).__init__(*args,**kwargs)

        self._is_display = True
        for f in self._form_class.base_fields.values():
            if not isinstance(f.widget,DisplayMixin):
                self._is_display = False
                break


    @property
    def form_class(self):
        return self._form_class

    @property
    def model(self):
        return self._form_class._meta.model

    @property
    def is_display(self):
        return self._is_display

    def get_boundfield(self,form,name):
        return BoundFormField(form,self,name)

    def get_initial(self):
        """
        guarantee a non-none value will be returned
        """
        if not self.initial:
            self.initial = self.form._meta.model()
        return self.initial

def FormFieldFactory(form_class):
    global class_id
    class_key = hashvalue("FormField<{}.{}>".format(form_class.__module__,form_class.__name__))
    if class_key not in field_classes:
        class_id += 1
        class_name = "FormField_{}".format(class_id)
        field_classes[class_key] = type(class_name,(FormField,),{"_form_class":form_class})
    return field_classes[class_key]

