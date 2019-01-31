from dpaw_utils.forms import filters

class DocumentFilter(filters.Filter):
    tag = filters.NumberFilter(field_name='tag',lookup_expr='exact')
    categoryid = filters.NumberFilter(field_name='category',lookup_expr='exact')
    modifierid = filters.NumberFilter(field_name='modifier',lookup_expr='exact')
    document_archived = filters.BooleanFilter(field_name='document_archived',lookup_expr='exact')
    modifiedrange = filters.DateRangeFilter(field_name="modified")
    q = filters.QFilter(fields=(("category__name","icontains"),("tag__name","icontains"),("custom_tag","icontains"),("modifier__username","icontains")))

