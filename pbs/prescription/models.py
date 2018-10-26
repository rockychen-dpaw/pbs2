@python_2_unicode_compatible
class Prescription(Audit):

    def get_absolute_url(self):
        return reverse('admin:prescription_prescription_detail',
                       args=(str(self.pk)))

@python_2_unicode_compatible
class PriorityJustification(Audit):
    _required_fields = ('rationale', 'priority')

@python_2_unicode_compatible
class RegionalObjective(Audit):
    _required_fields = ('region', 'impact', 'objectives')

@python_2_unicode_compatible
class Objective(Audit):
    _required_fields = ('objectives', )

@python_2_unicode_compatible
class SuccessCriteria(Audit):
    _required_fields = ('criteria', )

