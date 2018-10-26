class Context(Audit):
    _required_fields = ('statement', )

@python_2_unicode_compatible
class Action(Audit):
    _required_fields = ('details', 'pre_burn_resolved',
                        'pre_burn_explanation', 'pre_burn_completed',
                        'pre_burn_completer', 'day_of_burn_include',
                        'day_of_burn_completer', 'day_of_burn_completed',
                        'post_burn_completer', 'post_burn_completed')

@python_2_unicode_compatible
class Register(Audit):
    _required_fields = ('description', 'draft_consequence',
                        'draft_likelihood', 'treatments',
                        'final_consequence', 'final_likelihood')

@python_2_unicode_compatible
class Contingency(Audit):
    _required_fields = ('description', 'trigger')

@python_2_unicode_compatible
class Complexity(Audit):
    _required_fields = ('rating', 'rationale',)

