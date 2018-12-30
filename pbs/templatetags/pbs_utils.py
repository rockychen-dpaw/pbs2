from django.conf import settings
from django.shortcuts import resolve_url
from django import template


register = template.Library()


@register.simple_tag
def page_background():
    """
    Usage:
        Set a image as html page's background to indicate the runtime environment (dev or uat)
    """
    if settings.ENV_TYPE == "PROD":
        return ""
    elif settings.ENV_TYPE == "LOCAL":
        return "background-image:url('/static/img/local.png')"
    elif settings.ENV_TYPE == "DEV":
        return "background-image:url('/static/img/dev.png')"
    elif settings.ENV_TYPE == "UAT":
        return "background-image:url('/static/img/uat.png')"
    elif settings.ENV_TYPE == "TEST":
        return "background-image:url('/static/img/test.png')"
    elif settings.ENV_TYPE == "TRAINING":
        return "background-image:url('/static/img/training.png')"
    else:
        return "background-image:url('/static/img/dev.png')"


@register.simple_tag
def call_method(obj,method_name,*args,**kwargs):
    return getattr(obj,method_name)(*args,**kwargs)

@register.simple_tag
def setvar(obj):
    return obj

@register.simple_tag
def debug(obj,*args):
    import ipdb;ipdb.set_trace()
    return ""

