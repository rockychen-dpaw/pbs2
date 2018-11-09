import re

from django.urls import path 
import django.views.generic.edit as django_edit_view
import django.views.generic.list as django_list_view

class UrlpatternsMixin(object):

    @classmethod
    def urlpatterns(cls):
        if not hasattr(cls,"_urlpatterns"):
            setattr(cls,"_urlpatterns",cls._get_urlpatterns())
        return cls._urlpatterns

    @classmethod
    def _get_urlpatterns(cls):
        model_name = cls.model.__name__.lower()
        urlpatterns = None
        if issubclass(cls,django_edit_view.CreateView):
            urlpatterns=[path('{}/add/'.format(model_name), cls.as_view(),name='{}_create'.format(model_name))]
        elif issubclass(cls,django_edit_view.UpdateView):
            urlpatterns=[path('{}/<int:pk>/'.format(model_name), cls.as_view(),name='{}_update'.format(model_name))]
        elif issubclass(cls,django_edit_view.DeleteView):
            urlpatterns=[path('{}/<int:pk>/delete/'.format(model_name), cls.as_view(),name='{}_delete'.format(model_name))]
        elif issubclass(cls,django_list_view.ListView):
            urlpatterns=[path('{}/'.format(model_name), cls.as_view(),name='{}_list'.format(model_name))]
        else:
            urlpatterns = []

        extra_urlpatterns = cls._get_extra_urlpatterns()
        if extra_urlpatterns:
            urlpatterns.extend(extra_urlpatterns)

        return urlpatterns


    @classmethod
    def _get_extra_urlpatterns(cls):
        return None

class CreateView(UrlpatternsMixin,django_edit_view.CreateView):
    title = None
    def get_context_data(self,**kwargs):
        context_data = super(CreateView,self).get_context_data(**kwargs)
        context_data["title"] = self.title or "Add {}".format(self.model._meta.verbose_name)
        return context_data

class ListView(UrlpatternsMixin,django_list_view.ListView):
    title = None
    order_by_re = re.compile('[?&]order_by=([-+]?)([a-zA-Z0-9_\-]+)')
    listform_class = None
    fiter_class = None
    filterform_class = None

    def get_listform_class(self):
        return self.listform_class

    def get_filter_class(self):
        return self.filter_class

    def get_filterform_class(self):
        return self.filterform_class

    def get_context_data(self,**kwargs):
        context_data = super(ListView,self).get_context_data(**kwargs)
        context_data["title"] = self.title or "{} List".format(self.model._meta.verbose_name)
        pathinfo = self.request.META["QUERY_STRING"]
        sorting_status = None
        if pathinfo:
            m = self.order_by_re.search(pathinfo)
            if m:
                sorting_status = (m.group(2),False if m.group(1) == '-' else True)
                if m.start() == 0:
                    pathinfo = "?{}".format(pathinfo[m.end() + 1:])
                elif m.end() == len(pathinfo):
                    pathinfo = pathinfo[:m.start()]
                else:
                    pathinfo = "{}{}".format(pathinfo[:m.start()],pathinfo[m.end():])
        
        context_data["listform"] = self.get_listform_class()(initial_list=context_data.get("object_list"),url=pathinfo,sorting_status=sorting_status)
        context_data["filterform"] = self.get_filterform_class()()

        return context_data

