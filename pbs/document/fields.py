import os
import shutil
import subprocess

from django.forms import ValidationError
from django.db.models import FileField
from django.template.defaultfilters import filesizeformat

from io import BytesIO
import tempfile
from south.modelsinspector import add_introspection_rules


add_introspection_rules(
    [], ["^pbs\.document\.models\.ContentTypeRestrictedFileField"])
