from django.utils import timezone
from django import forms

def coerce_TrueFalse(value):
    if value is None or value == '':
        return None
    if isinstance(value,basestring):
        return value == "True"
    return value

def coerce_YesNo(value):
    if value is None or value == '':
        return None
    if isinstance(value,basestring):
        return value == "Yes"
    return value

def coerce_int(value):
    if value is None or value == '':
        return None
    return int(value)


class FinancialYear(object):
    def __init__(self):
        now = timezone.now()
        if now.month >= 7:
            self.current_fyear = now.year
        else:
            self.current_fyear = now.year - 1

    @classmethod
    def format(cls,fyear):
        return "{}/{}".format(fyear,fyear + 1)


    def current(self,formated=False):
        if formated:
            return self.format(self.current_fyear)
        else:
            return self.current_fyear

    def next(self,formated=False):
        if formated:
            return self.format(self.current_fyear + 1)
        else:
            return self.current_fyear + 1

    def previous(self,formated=False):
        if formated:
            return self.format(self.current_fyear - 1)
        else:
            return self.current_fyear - 1

    def get(self,offset,formated=False):
        if formated:
            return self.format(self.current_fyear + offset)
        else:
            return self.current_fyear + offset

    @classmethod
    def parse(cls,fyear,formated=False):
        if isinstance(fyear,str):
            fyears = fyear.split('/')
            if len(fyears) == 1 :
                try:
                    fyear = int(fyear)
                except:
                    raise forms.ValidationError("Financial Year must be consecutive years and in the format '2015/2016',or a year")
            else:
                if len(fyears) != 2 or not(all(fyears)):
                    raise forms.ValidationError("Financial Year must be consecutive years and in the format '2015/2016'")
                try:
                    fyears = [int(y.strip()) for y in fyears]
                except:
                    raise forms.ValidationError("Financial Year must be consecutive years and in the format '2015/2016'")

                if fyears[0] + 1 != fyears[1]:
                    raise forms.ValidationError("Financial Year must be consecutive years and in the format '2015/2016'")

                fyear = fyears[0]
        else:
            try:
                fyear = int(fyear)
            except:
                raise forms.ValidationError("Financial Year must be consecutive years and in the format '2015/2016',or a year")
        
        if formated:
            return cls.format(fyear)
        else:
            return fyear


    def is_current(self,fyear):
        return self.current_fyear == self.parse(fyear)

    def is_future(self,fyear):
        return self.current_fyear < self.parse(fyear)

    def is_before(self,fyear):
        return self.current_fyear > self.parse(fyear)

    def range(self,start_offset,end_offset,formated=False):
        """
        start_offset included
        end_offset included
        """
        if formated:
            return [self.format(self.current_fyear + y) for y in range(start_offset,end_offset + 1) ]
        else:
            return [(self.current_fyear + y) for y in range(start_offset,end_offset + 1) ]

    def options(self,start_offset,end_offset):
        """
        start_offset included
        end_offset included
        """
        return [(self.format(self.current_fyear + y),self.format(self.current_fyear + y)) for y in range(start_offset,end_offset + 1) ]


    def __str__(self):
        return "{}/{}".format(self.current_fyear,self.current_fyear + 1)
