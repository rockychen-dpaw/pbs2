"""pbs_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('docs/', include('django.contrib.admindocs.urls')),
    path('', include('django.contrib.auth.urls'))
]
import pbs.views
import pbs.prescription.urls
import pbs.report.urls
import pbs.risk.urls
import pbs.document.urls
import pbs.stakeholder.urls

from tastypie.api import Api

handler500 = pbs.views.handler500
handler404 = pbs.views.handler404

urlpatterns = urlpatterns + [
    path("admin/",admin.site.urls),
    path("prescription/",include(pbs.prescription.urls,namespace="prescription")),
    path("prescription/",include(pbs.report.urls,namespace="report")),
    path("risk/",include(pbs.risk.urls,namespace="risk")),
    path("document/",include(pbs.document.urls,namespace="document")),
    path("stakeholder/",include(pbs.stakeholder.urls,namespace="stakeholder"))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
for p in urlpatterns:
    print(p)
