import re

from django.urls import path 
from django.http import Http404,HttpResponse,HttpResponseForbidden
import django.views.generic.edit as django_edit_view
import django.views.generic.list as django_list_view

class RequestActionMixin(object):
    action = None
    default_action = None
    def get_action(self,action_name):
        raise Exception('Not Implemented')

    def has_permission(self,request,action_name):
        return self.get_action(action_name).has_permission(request.user) 

    def dispatch(self,request, *args, **kwargs):
        handler = None
        try:
            if request.method == "GET":
                if "action" in request.GET:
                    self.action = request.GET["action"]
                    handler = "{}_{}".format(self.action,"get")
            else:
                if "action" in request.POST:
                    self.action = request.POST["action"]
                    handler = "{}_{}".format(self.action,"post")

            if self.action and self.action != self.default_action:
                if not self.has_permission(request,self.action):
                    return HttpResponseForbidden('Not authorised.')
                if hasattr(self,handler):
                    return getattr(self,handler)(request,*args,**kwargs)
                else:
                    raise Http404("Action '{}' is not supported.".format(self.action))

            return super(RequestActionMixin,self).dispatch(request,*args,**kwargs)
        except Http404:
            raise
        except Exception as ex:
            return HttpResponse(status=500,reason=str(ex),content=str(ex))

class RequestUrl(object):
    ordering_re = re.compile('[?&]order_by=([-+]?)([a-zA-Z0-9_\-]+)')
    action_re = re.compile('[?&]action=([a-zA-Z0-9_\-]+)')
    paging_re = re.compile('[?&]page=([0-9]+)')

    qs_without_ordering = None
    qs_without_paging = None
    current_page = None
    _sorting_status = None
    current_action = None

    def __init__(self,request):
        self.request = request

    @property
    def path(self):
        return self.request.path

    def _get_request_parameter(self,param_re,qs=None,repeat=False,remove=True):
        """
        remove: true, parameter will be removed in the returned querystring
        Return 
            repeat = False,(querystring,(matching_string,subgroups)) 
            repeat = True,(querystring,[(matching_string,subgroups),...]) 
        """
        qs = qs or self.request.META["QUERY_STRING"]
        if qs:
            qs = "?{}".format(qs)
        if repeat:
            pos = 0
            m =  param_re.search(qs,pos)
            if not m:
                return (qs,None)
            matches = []
            while(m):
                matches.append((m.group(0),m.groups()))
                if remove:
                    if m.start() == 0:
                        if m.end() == len(qs):
                            qs = ""
                            break
                        else:
                            qs = "?{}".format(qs[m.end() + 1:])
                            pos = 0
                    elif m.end() == len(qs):
                        qs = qs[:m.start()]
                        break
                    else:
                        qs = "{}{}".format(qs[:m.start()],qs[m.end():])
                        pos = m.start()
                else:
                    pos = m.end()

                m =  param_re.search(qs,pos)
            return (qs,matches)
        else:
            m = param_re.search(qs)
            if m:
                if remove:
                    if m.start() == 0:
                        if m.end() == len(qs):
                            qs = ""
                        else:
                            qs = "?{}".format(qs[m.end() + 1:])
                    elif m.end() == len(qs):
                        qs = qs[:m.start()]
                    else:
                        qs = "{}{}".format(qs[:m.start()],qs[m.end():])
                return (qs,(m.group(0),m.groups()))
            else:
                return (qs,None)

    def _parse_ordering(self):
        if self.qs_without_ordering is None:
            self.qs_without_ordering,groups = self._get_request_parameter(self.ordering_re,remove=True)
            if groups:
                self._sorting_status = (groups[1][1],False if groups[1][0] == '-' else True )
            else:
                self._sorting_status = None

    @property
    def sorting_status(self):
        self._parse_ordering()
        return self._sorting_status

    @property
    def sorting_clause(self):
        self._parse_ordering()
        if self._sorting_status:
            return "{}{}".format("" if self._sorting_status[1] else "-" ,self._sorting_status[0])
        else:
            return None

    def _parse_paging(self):
        if self.qs_without_paging is None:
            self.qs_without_paging,groups = self._get_request_parameter(self.paging_re,remove=True)
            if groups:
                self.current_page = int(groups[1][0])
            else:
                self.current_page = None

    def querystring(self,ordering=None,page=None):
        if ordering is not None:
            self._parse_ordering()
            if not ordering:
                return self.qs_without_ordering
            elif self.qs_without_ordering:
                return "{}&order_by={}".format(self.qs_without_ordering,ordering)
            else:
                return "?order_by={}".format(ordering)
        elif page is not None:
            self._parse_paging()
            if self.qs_without_paging:
                return "{}&page={}".format(self.qs_without_paging,page)
            else:
                return "?page={}".format(page)
        else:
            return self.request.META["QUERY_STRING"]

    @property
    def querystring_without_ordering(self):
        self._parse_ordering()
        return self.qs_without_ordering

    @property
    def querystring_without_paging(self):
        self._parse_paging()
        return self.qs_without_paging

class UrlpatternsMixin(object):
    urlpattern = None
    urlname = None

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
            urlpatterns=[path((cls.urlpattern or '{}/add/').format(model_name), cls.as_view(),name=(cls.urlname or '{}_create').format(model_name))]
        elif issubclass(cls,django_edit_view.UpdateView):
            urlpatterns=[path((cls.urlpattern or '{}/<int:pk>/').format(model_name), cls.as_view(),name=(cls.urlname or '{}_update').format(model_name))]
        elif issubclass(cls,django_edit_view.DeleteView):
            urlpatterns=[path((cls.urlpattern or '{}/<int:pk>/delete/').format(model_name), cls.as_view(),name=(cls.urlname or '{}_delete').format(model_name))]
        elif issubclass(cls,django_list_view.ListView):
            urlpatterns=[path((cls.urlpattern or '{}/').format(model_name), cls.as_view(),name=(cls.urlname or '{}_list').format(model_name))]
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
    def get_form_kwargs(self):
        kwargs = super(CreateView,self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self,**kwargs):
        context_data = super(CreateView,self).get_context_data(**kwargs)
        context_data["title"] = self.title or "Add {}".format(self.model._meta.verbose_name)
        return context_data

class ReadonlyView(UrlpatternsMixin,django_edit_view.UpdateView):
    title = None

    def get_form_kwargs(self):
        kwargs = super(ReadonlyView,self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self,**kwargs):
        context_data = super(ReadonlyView,self).get_context_data(**kwargs)
        context_data["title"] = self.title or self.model._meta.verbose_name
        return context_data

    def post(self,request,*args,**kwargs):
        return HttpResponseForbidden()

    def put(self,request,*args,**kwargs):
        return HttpResponseForbidden()

class UpdateView(UrlpatternsMixin,django_edit_view.UpdateView):
    title = None

    def get_form_kwargs(self):
        kwargs = super(UpdateView,self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self,**kwargs):
        context_data = super(UpdateView,self).get_context_data(**kwargs)
        context_data["title"] = self.title or "Update {}".format(self.model._meta.verbose_name)
        return context_data

class ListView(RequestActionMixin,UrlpatternsMixin,django_list_view.ListView):
    default_action = "search"
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

    def create_filterform(self):
        filterform = self.get_filterform_class()(data=self.request.GET,request=self.request)
        return filterform

    def get_filterform(self):
        if not hasattr(self,"_filterform"):
            self._filterform = self.create_filterform()
        return self._filterform

    def get_queryset(self):
        filterform = self.get_filterform()
        if filterform.is_valid():
            data_filter = self.get_filter_class()(filterform,request=self.request)
            qs = data_filter.qs
            ordering = self.get_ordering()
            if ordering:
                qs = qs.order_by(ordering)
            return qs
        else:
            return filterform._meta.objects.none()

    def get_queryset_4_selected(self,request):
        if request.POST.get("select_all") == "true" :
            filterform = self.get_filterform_class()(data=self.request.POST,request=self.request)
            if not filterform.is_valid():
                raise http.HttpResponseServerError()

            data_filter = self.get_filter_class()(filterform,request=self.request)
            queryset = data_filter.qs
            print("All {} records are selected.".format(len(queryset)))
        else:
            pks = [int(pk) for pk in request.POST.getlist("selectedpks")]
            if pks:
                queryset = Prescription.objects.filter(pk__in=pks)
            else:
                raise Exception("No Prescribed Fire Plan is selected.")

            print("{} records are selected.".format(len(queryset)))
        return queryset

    def get_ordering(self):
        return self.requesturl.sorting_clause

    def dispatch(self,request, *args, **kwargs):
        self.requesturl = RequestUrl(request)
        return super(ListView,self).dispatch(request,*args,**kwargs)

    def post(self,request,*args,**kwargs):
        raise Http404("Post method is not supported.")

    def get_context_data(self,**kwargs):
        context_data = super(ListView,self).get_context_data(**kwargs)
        context_data["title"] = self.title or "{} List".format(self.model._meta.verbose_name)
        context_data["listform"] = self.get_listform_class()(initial_list=context_data.get("object_list"),request=self.request,requesturl = self.requesturl)
        context_data["requesturl"] = self.requesturl
        context_data["filterform"] = self.get_filterform()

        return context_data

