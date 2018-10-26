from django.urls import include, path

from .views import PrescripionView

urlpatterns = [
    path('prescription', include('django.contrib.admindocs.urls')),
]
