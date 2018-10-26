import logging
import sys

from django.template import Context, loader
from django.http import HttpResponseServerError

log = logging.getLogger(__name__)

# Create your views here.
def handler500(request):
    context = {'request': request}
    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render(Context(context)))


def handler404(request):
    context = {'request': request}
    t = loader.get_template('404.html')
    return HttpResponseServerError(t.render(Context(context)))
