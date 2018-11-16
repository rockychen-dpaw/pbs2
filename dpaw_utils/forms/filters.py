from django.db import models

from django_filters.rest_framework import *

class Filter(FilterSet):
    def __init__(self,form,request=None,queryset=None):
        queryset = queryset or form._meta.model.objects.all()
        super(Filter,self).__init__(request,queryset=queryset)
        self._form = form

    def filter_queryset(self, queryset):
        """
        Filter the queryset with the underlying form's `cleaned_data`. You must
        call `is_valid()` or `errors` before calling this method.

        This method should be overridden if additional filtering needs to be
        applied to the queryset before it is cached.
        """
        for name, value in self.form.cleaned_data.items():
            if value is None:
                continue
            elif name not in self.filters:
                continue
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(queryset, models.QuerySet), \
                "Expected '%s.%s' to return a QuerySet, but got a %s instead." \
                % (type(self).__name__, name, type(queryset).__name__)
        return queryset

