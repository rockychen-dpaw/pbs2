import traceback

from django import forms
from django.core.cache import caches
from django.urls import reverse
from django.db import models
from django.utils.html import mark_safe

from ..utils import hashvalue


to_str = lambda o: "" if o is None else str(o)

class DisplayMixin(forms.Widget):
    pass

class DisplayWidget(DisplayMixin,forms.Widget):
    def __deepcopy__(self, memo):
        return self

class HtmlTag(DisplayWidget):
    template = "<{0} {1}>{2}</{0}>"
    def __init__(self,tag,attrs = None,value=None):
        self._tag = tag
        self._value = value
        self._attrs = attrs
    def render(self):
        if self._attrs:
            attrs = " ".join(["{}=\"{}\"".format(key,value) for key,value in self._attrs.items()])
        else:
            attrs = ""
        if self._value:
            if isinstance(self._value,HtmlTag):
                value = self._value.render()
            else:
                value = self._value
        else:
            value = ""
        return self.template.format(self._tag,attrs,value)

    @property
    def html(self):
        return mark_safe(self.render())


class TextDisplay(DisplayWidget):
    def render(self,name,value,attrs=None,renderer=None):
        return to_str(value)

class FinancialYearDisplay(DisplayWidget):
    def render(self,name,value,attrs=None,renderer=None):
        value = int(value)
        return "{}/{}".format(value,value+1)

class DmsCoordinateDisplay(DisplayWidget):
    def render(self,name,value,attrs=None,renderer=None):
        if value:

            c=LatLon.LatLon(LatLon.Longitude(value.get_x()), LatLon.Latitude(value.get_y()))
            latlon = c.to_string('d% %m% %S% %H')
            lon = latlon[0].split(' ')
            lat = latlon[1].split(' ')
        
            # need to format float number (seconds) to 1 dp
            lon[2] = str(round(eval(lon[2]), 1))
            lat[2] = str(round(eval(lat[2]), 1))
        
            # Degrees Minutes Seconds Hemisphere
            lat_str = lat[0] + u'\N{DEGREE SIGN} ' + lat[1].zfill(2) + '\' ' + lat[2].zfill(4) + '\" ' + lat[3]
            lon_str = lon[0] + u'\N{DEGREE SIGN} ' + lon[1].zfill(2) + '\' ' + lon[2].zfill(4) + '\" ' + lon[3]
        
            return 'Lat/Lon ' + lat_str + ', ' + lon_str
        else:
            return ""

class DatetimeDisplay(DisplayWidget):
    def __init__(self,date_format="%d/%m/%Y %H:%M:%S"):
        super(DatetimeDisplay,self).__init__()
        self.date_format = date_format or "%d/%m/%Y %H:%M:%S"

    def render(self,name,value,attrs=None,renderer=None):
        if value:
            return value.strftime(self.date_format)
        else:
            return ""

class Hyperlink(DisplayWidget):
    def __init__(self,**kwargs):
        super(Hyperlink,self).__init__(**kwargs)
        self.widget = self.widget_class(**kwargs)

    def prepare_initial_data(self,initial_data,name):
        value = initial_data.get(name)
        if not self.ids:
            #no configured 
            return (value,None)
            
        url = None
        kwargs = {}
        for f in self.ids:
            val = initial_data.get(f[0])
            if val is None:
                #can't find value for url parameter, no link can be generated
                kwargs = None
                break;
            elif isinstance(val,models.Model):
                kwargs[f[1]] = val.pk
            else:
                kwargs[f[1]] = val
        if kwargs:
            return (value,reverse(self.url_name,kwargs=kwargs))
        else:
            return(value,None)

    def render(self,name,value,attrs=None,renderer=None):
        if value :
            if value[1]:
                return "<a href='{}'>{}</a>".format(value[1],self.widget.render(name,value[0],attrs,renderer)) if value else ""
            else:
                return self.widget.render(name,value[0],attrs,renderer)
        else:
            return ""

widget_classes = {}
widget_class_id = 0
def HyperlinkFactory(field_name,url_name,widget_class=TextDisplay,ids=[("id","pk")],baseclass=Hyperlink):
    global widget_class_id
    key = hashvalue("{}{}{}".format(baseclass.__name__,url_name,field_name))
    cls = widget_classes.get(key)
    if not cls:
        widget_class_id += 1
        class_name = "{}_{}".format(baseclass.__name__,widget_class_id)
        cls = type(class_name,(baseclass,),{"url_name":url_name,"widget_class":widget_class,"ids":ids})
        widget_classes[key] = cls
    return cls


class TemplateDisplay(DisplayWidget):
    def __init__(self,widget,template):
        super(TemplateDisplay,self).__init__()
        self.template = template
        self.widget = widget

    def render(self,name,value,attrs=None,renderer=None):
        if not self.template or not value:
            return self.widget.render(name,value,attrs,renderer)
        return mark_safe(self.template.format(self.widget.render(name,value,attrs,renderer)))


class DatetimeInput(forms.TextInput):
    def render(self,name,value,attrs=None,renderer=None):
        html = super(DatetimeInput,self).render(name,value,attrs)
        datetime_picker = """
        <script type="text/javascript">
            $("#{}").datetimepicker({{ 
                format: "Y-m-d H:i" ,
                maxDate:true,
                step: 30,
            }}); 
        </script>
        """.format(attrs["id"])
        return mark_safe("{}{}".format(html,datetime_picker))


class TemplateWidgetMixin(object):
    template = ""

    def render(self,name,value,attrs=None,renderer=None):
        widget_html = super(TemplateWidgetMixin,self).render(name,value,attrs)
        return mark_safe(self.template.format(widget_html))


def TemplateWidgetFactory(widget_class,template):
    global widget_class_id
    key = hashvalue("{}{}{}".format(widget_class.__name__,TemplateWidgetMixin.__name__,template))
    cls = widget_classes.get(key)
    if not cls:
        widget_class_id += 1
        class_name = "{}_template_{}".format(widget_class.__name__,widget_class_id)
        cls = type(class_name,(TemplateWidgetMixin,widget_class),{"template":template})
        widget_classes[key] = cls
    return cls


class SwitchWidgetMixin(object):
    html = ""
    switch_template = ""
    true_value = True
    reverse = False
    html_id = None

    def render(self,name,value,attrs=None,renderer=None):
        value_str = str(value) if value is not None else ""
        if not self.html_id:
            html_id = "{}_related_html".format( attrs.get("id"))
            wrapped_html = "<span id='{}' {} >{}</span>".format(html_id,"style='display:none'" if (not self.reverse and value_str != self.true_value) or (self.reverse and value_str == self.true_value) else "" ,self.html)
        else:
            html_id = self.html_id
            if (not self.reverse and value_str == self.true_value) or (self.reverse and value_str != self.true_value):
                wrapped_html = ""
            else:
                wrapped_html = """
                <script type="text/javascript">
                $(document).ready(function() {{
                    $('#{}').hide()
                }})
                </script>
                """.format(html_id)
        
        show_html = "$('#{0}').show();".format(html_id)
        hide_html = "$('#{0}').hide();".format(html_id)

        attrs = attrs or {}
        if isinstance(self,forms.RadioSelect):
            attrs["onclick"]="""
                if (this.value === '{0}') {{
                    {1}
                }} else {{
                    {2}
                }}
            """.format(self.true_value,hide_html if self.reverse else show_html,show_html if self.reverse else hide_html)
        elif isinstance(self,forms.CheckboxInput):
            attrs["onclick"]="""
                if (this.checked) {{
                    {0}
                }} else {{
                    {1}
                }}
            """.format(hide_html if self.reverse else show_html,show_html if self.reverse else hide_html)
        elif isinstance(self,forms.Select):
            attrs["onchange"]="""
                if (this.value === '{0}') {{
                    {1}
                }} else {{
                    {2}
                }}
            """.format(self.true_value,hide_html if self.reverse else show_html,show_html if self.reverse else hide_html)
        else:
            raise Exception("Not implemented")

        widget_html = super(SwitchWidgetMixin,self).render(name,value,attrs)
        return mark_safe(self.switch_template.format(widget_html,wrapped_html))

def SwitchWidgetFactory(widget_class,html=None,true_value=True,template="{0}<br>{1}",html_id=None,reverse=False):
    global widget_class_id
    if html_id:
        template="""{0}
        {1}
        """
    key = hashvalue("{}{}{}{}{}{}".format(widget_class.__name__,true_value,template,html,html_id,reverse))
    cls = widget_classes.get(key)
    true_value = str(true_value) if true_value is not None else ""
    if not cls:
        widget_class_id += 1
        class_name = "{}_{}".format(widget_class.__name__,widget_class_id)
        cls = type(class_name,(SwitchWidgetMixin,widget_class),{"switch_template":template,"true_value":true_value,"html":html,"reverse":reverse,"html_id":html_id})
        widget_classes[key] = cls
    return cls

class ChoiceDisplay(DisplayWidget):
    choices = None
    marked_safe = False
            
    def _render(self,name,value,attrs=None,renderer=None):
        try:
            result = self.__class__.choices[value]
        except KeyError as ex:
            result = self.__class__.choices.get("__default__",value)
        if result is None:
            return ""
        if self.marked_safe:
            return mark_safe(result)
        else:
            return result

    def _render_template(self,name,value,attrs=None,renderer=None):
        try:
            result = self.__class__.choices[value]
        except KeyError as ex:
            result = self.__class__.choices.get("__default__",value)
        if result is None:
            return ""
        if self.marked_safe:
            return mark_safe(result.format(value))
        else:
            return result.format(value)


def ChoiceWidgetFactory(name,choices,marked_safe=False,template=False):
    global widget_class_id
    widget_class = ChoiceDisplay
    if isinstance(choices,list) or isinstance(choices,tuple):
        choices = dict(choices)
    elif isinstance(choices,dict):
        choices = choices
    else:
        raise Exception("Choices must be a dictionary or can be converted to a  dictionary.")

    key = hashvalue("{}{}".format(widget_class.__name__,name))
    cls = widget_classes.get(key)
    if not cls:
        widget_class_id += 1
        class_name = "{}_{}".format(widget_class.__name__,name)
        if template:
            cls = type(class_name,(widget_class,),{"choices":choices,"marked_safe":marked_safe,"render":ChoiceDisplay._render_template})
        else:
            cls = type(class_name,(widget_class,),{"choices":choices,"marked_safe":marked_safe,"render":ChoiceDisplay._render})
        widget_classes[key] = cls
    return cls

ImgBooleanDisplay = ChoiceWidgetFactory("ImgBooleanDisplay",{
    True:"<img src=\"/static/img/icon-yes.gif\">",
    False:"<img src=\"/static/img/icon-no.gif\"/>",
    None:""
},True)

TextBooleanDisplay = ChoiceWidgetFactory("TextBooleanDisplay",{
    True:"Yes",
    False:"No",
    None:""
})

class NullBooleanSelect(forms.widgets.Select):
    def __init__(self, attrs=None):
        choices = (
            ('', 'Unknown'),
            ('True', 'Yes'),
            ('False','No'),
        )
        super(NullBooleanSelect,self).__init__(attrs, choices)

    def format_value(self, value):
        return "" if value is None else str(value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        return None if (value == "" or value is None) else (True if value == 'True' else False) 


html_id_seq = 0
class SelectableSelect(forms.Select):
    def __init__(self,**kwargs):
        if kwargs.get("attrs"):
            if kwargs["attrs"].get("class"):
                kwargs["attrs"]["class"] = "{} selectpicker dropup".format(kwargs["attrs"]["class"])
            else:
                kwargs["attrs"]["class"] = "selectpicker dropup"
        else:
            kwargs["attrs"] = {"class":"selectpicker dropup"}
        super(SelectableSelect,self).__init__(**kwargs)


    def render(self,name,value,attrs=None,renderer=None):
        global html_id_seq
        html_id = attrs.get("id",None) if attrs else None
        if not html_id:
            html_id_seq += 1
            html_id = "auto_id_{}".format(html_id_seq)
            if attrs is None:
                attrs = {"id":html_id}
            else:
                attrs["id"] = html_id

        html = super(SelectableSelect,self).render(name,value,attrs)


        return mark_safe(u"""
        {}
        <script type="text/javascript">
            $("#{}").selectpicker({{
              style: 'btn-default',
              size: 6,
              liveSearch: true,
              dropupAuto: false,
              closeOnDateSelect: true,
            }});
        </script>
        """.format(html,html_id))

def ChoiceFieldRendererFactory(outer_html = None,inner_html = None,layout = None):
    """
    layout: none, horizontal,vertical
    outer_html: used if layout is None
    inner_html:used in layout is None
    """
    global widget_class_id

    if layout == "vertical":
        return forms.widgets.ChoiceFieldRenderer

    if layout == "horizontal":
        outer_html = '<ul{id_attr} style="padding:0px;margin:0px">{content}</ul>'
        inner_html = '<li style="list-style-type:none;padding:0px 15px 0px 0px;display:inline;">{choice_value}{sub_widgets}</li>'

    renderer_class = forms.widgets.CheckboxFieldRenderer

    key = hashvalue("ChoiceFieldRenderer<{}.{}{}{}>".format(renderer_class.__module__,renderer_class.__name__,outer_html,inner_html))
    cls = widget_classes.get(key)
    if not cls:
        widget_class_id += 1
        class_name = "{}_{}".format(renderer_class.__name__,widget_class_id)
        cls = type(class_name,(renderer_class,),{"outer_html":outer_html,"inner_html":inner_html})
        widget_classes[key] = cls
    return cls


def DisplayWidgetFactory(widget_class):
    """
    Use other widget as display widget.
    """
    global widget_class_id

    key = hashvalue("DisplayWidget<{}>".format(widget_class.__module__,widget_class.__name__))
    cls = widget_classes.get(key)
    if not cls:
        widget_class_id += 1
        class_name = "{}_{}".format(widget_class.__name__,widget_class_id)
        cls = type(class_name,(DisplayMixin,widget_class),{})
        widget_classes[key] = cls
    return cls


class DropdownMenuSelectMultiple(forms.widgets.SelectMultiple):
    def render(self, name, value, attrs=None, renderer=None):
        if not attrs:
            attrs={"style":"display:none"}
        elif attrs.get("style"):
            attrs["style"]="{};display:none".format(attrs["style"])
        else:
            attrs["style"]="display:none"

        attrs["id"] = name
        html = super(DropdownMenuSelectMultiple,self).render("",value,attrs,renderer)
        html_id = attrs.get("id")
        if html_id:
            html = """
            {1}
            <script type="text/javascript">
                $(document).ready(function(){{
                    $("#{0}").multiselect({{
                        buttonText: function() {{
                            return $("#{0}").attr('title');
                        }},
                        buttonClass: "btn btn-small",
                        checkboxName: $("#{0}").attr("id")
                    }});
                }})
            </script>
            """.format(html_id,html)
        return html
