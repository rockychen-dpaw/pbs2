from types import MethodType

from .forms import ModelForm

def _dummy_full_clean(self):
    pass

class FilterForm(ModelForm):
    def __init__(self, *args,**kwargs):
        instance = None
        if "instance" not in kwargs:
            instance = self._meta.model()
            kwargs["instance"] = instance
            #set all field to None
            for field in instance._meta.fields:
                setattr(instance,field.name,None)
        else:
            instance = kwargs["instance"]

        #replace full_clean method because filter instance doesn't require clean logic
        instance.full_clean = MethodType(_dummy_full_clean,instance)
    
        if "auto_id" not in kwargs:
            kwargs["auto_id"] = "id_filter_%s"

        super(FilterForm,self).__init__(*args,**kwargs)

    def save(self, commit=True):
        raise NotImplementedError()

    def validate_unique(self):
        pass
        
    class Meta:
        pass
