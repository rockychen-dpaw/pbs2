
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from pbs.prescription.models import (PrescriptionCreateView,)
from pbs.prescription.forms import (PrescriptionCreateForm,)

class PrescriptionCreateView(CreateView):
    model = Prescritpion
    form_class = PrescriptionCreateForm

