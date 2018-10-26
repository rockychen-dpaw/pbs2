class PostBurnChecklist(Audit):
    _required_fields = ('completed_on', 'completed_by')

class AreaAchievement(Audit):
    _required_fields = ('ignition', 'ignition_types',
                        'area_treated', 'area_estimate')

class Evaluation(Audit):
    _required_fields = ('achieved', 'summary')

class ProposedAction(Audit):
    _required_fields = ('observations', 'action')

