@python_2_unicode_compatible
class RoadSegment(Way):
    _required_fields = ('name', 'road_type',)

@python_2_unicode_compatible
class TrailSegment(Way):
    _required_fields = ('name', )



@python_2_unicode_compatible
class LightingSequence(Audit):
    _required_fields = ('seqno', 'cellname', 'strategies',
                        'fuel_description', 'fuel_age', 'fuel_age_unknown',
                        'ignition_types', 'ffdi_min', 'ffdi_max',
                        'ros_min', 'ros_max', 'wind_min', 'wind_max',
                        'wind_dir')

@python_2_unicode_compatible
class ExclusionArea(Audit):
    _required_fields = ('location', 'description',
                        'detail')
