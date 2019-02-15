from django.forms import fields as django_fields
from ..widgets import widgets

class AggregateField(django_fields.Field):
    def __init__(self,form_field_name,*args,**kwargs):
        if "widget" not in kwargs:
            kwargs["widget"] = widgets.TextDisplay()
        super(AggregateField,self).__init__(*args,**kwargs)
        self.field_name = form_field_name

    def __deepcopy__(self, memo):
        return self

    def value(self,listform):
        if not listform:
            return None 
        result = None
        for form in listform:
            result = self.aggregate(result,form[self.field_name].value())

        return result


    def aggregate(aggregate_value,value):
        raise NotImplementedError("Not implemented")

class SummaryField(AggregateField):
    
    def aggregate(self,aggregate_value,value):
        if value:
            if aggregate_value:
                return aggregate_value + value
            else:
                return value
        else:
            return aggregate_value

