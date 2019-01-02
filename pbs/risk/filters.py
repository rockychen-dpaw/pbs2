from dpaw_utils.forms import filters

class ComplexityFilter(filters.Filter):
    factor = filters.CharFilter(field_name='factor', lookup_expr='exact')

