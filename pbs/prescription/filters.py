
from dpaw_utils.forms import filters

class PrescriptionFilter(filters.Filter):
    region = filters.NumberFilter(field_name='region', lookup_expr='in')
    district = filters.NumberFilter(field_name='district', lookup_expr='in')
    financial_year = filters.NumberFilter(field_name='financial_year', lookup_expr='in')
    contentious = filters.NumberFilter(field_name='contentious', lookup_expr='in')
    aircraft_burn = filters.NumberFilter(field_name='aircraft_burn', lookup_expr='in')
    priority = filters.NumberFilter(field_name='priority', lookup_expr='in')
    planning_status = filters.NumberFilter(field_name='planning_status', lookup_expr='in')
    endorsement_status = filters.NumberFilter(field_name='endorsement_status', lookup_expr='in')
    approval_status = filters.NumberFilter(field_name='approval_status', lookup_expr='in')
    ignition_status = filters.NumberFilter(field_name='ignition_status', lookup_expr='in')
    status = filters.NumberFilter(field_name='status', lookup_expr='in')
    contingencies_migrated = filters.NumberFilter(field_name='contingencies_migrated', lookup_expr='in')

