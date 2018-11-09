
from dpaw_utils.views import (CreateView,ListView)

from ..models import (Prescription,)
from ..forms import (PrescriptionCreateForm,PrescriptionFilterForm,PrescriptionListForm)
from ..filters import (PrescriptionFilter,)

class PrescriptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionCreateForm
    template_name_suffix = "_create_form"

class PrescriptionListView(ListView):
    title = "Regional Overview"
    listform_class = PrescriptionListForm
    filterform_class = PrescriptionFilterForm
    filter_class = PrescriptionFilter
    model = Prescription
    paginate_by=1
    

