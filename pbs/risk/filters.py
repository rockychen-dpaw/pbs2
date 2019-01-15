from dpaw_utils.forms import filters

class ComplexityFilter(filters.Filter):
    factor = filters.CharFilter(field_name='factor', lookup_expr='exact')

class ActionFilter(filters.Filter):
    relevant = filters.CharFilter(field_name='relevant', lookup_expr='exact')
    category = filters.NumberFilter(field_name='risk__category',lookup_expr='exact')

