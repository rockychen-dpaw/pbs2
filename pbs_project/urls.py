from django_downloadview import ObjectDownloadView
from pbs.document.models import Document
from pbs.sites import site
from pbs.forms import PbsPasswordResetForm

from pbs.review.api import PrescribedBurnResource

# Define the simplest possible view for Document uploads.
document_download = ObjectDownloadView.as_view(model=Document, file_field='document')

v1_api = Api(api_name='v1')
v1_api.register(PrescribedBurnResource())

urlpatterns = urlpatterns + patterns('',
    url(r'^select2/', include('django_select2.urls')),
    (r'^', include('pbs.registration.urls')),
    # the password reset must come before site.urls, site.urls match all
    (r'^', include(site.urls)),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset',
        {'password_reset_form': PbsPasswordResetForm}, name='password_reset'),
    url(r'^chaining/', include('smart_selects.urls')),
    url('^documents/(?P<pk>\d+)/download$', document_download, name='document_download'),

    url(r'^api/', include(v1_api.urls)),
)
