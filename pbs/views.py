import logging
import sys

from django.template import Context, loader
from django.http import HttpResponseServerError

from .forms import LIST_ACTIONS,FORM_ACTIONS

log = logging.getLogger(__name__)

# Create your views here.
def handler500(request):
    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(request=request))


def handler404(request):
    t = loader.get_template('404.html')
    return HttpResponseServerError(t.render(request=request))

class ListActionMixin(object):
    def get_action(self,action_name):
        return LIST_ACTIONS.get(action_name)

class FormActionMixin(object):
    def get_action(self,action_name):
        return FORM_ACTIONS.get(action_name)

