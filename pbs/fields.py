from dpaw_utils.forms.fields import (ChoiceFieldFactory,)

import pbs.utils

BooleanChoiceField = ChoiceFieldFactory([
    (True,"Yes"),
    (False,"No")
],field_params={"coerce":pbs.utils.coerce_TrueFalse,'empty_value':None})
