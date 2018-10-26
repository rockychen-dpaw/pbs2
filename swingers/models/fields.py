from django.db.models import FileField
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

from south.modelsinspector import add_introspection_rules

import magic


class ContentTypeRestrictedFileField(FileField):
    """
    Same as Django's normal FileField, but you can specify:
    * content_types - a list containing allowed MIME types.
        Example: ['application/pdf', 'image/jpeg']
    * max_upload_size - a number indicating the maximum file size
        allowed for upload.

        2.5MB - 2621440
        5MB - 5242880
        10MB - 10485760
        20MB - 20971520
        50MB - 5242880
        100MB - 104857600
        250MB - 214958080
        500MB - 429916160
    """
    default_error_messages = {
        'filetype': 'That file type is not permitted.',
        'max_size': 'Maximum filesize is {0} (actual filesize was {1}).'
    }

    def __init__(self, content_types=None, max_upload_size=None, *args,
                 **kwargs):
        self.content_types = content_types
        self.max_upload_size = max_upload_size
        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        f = super(ContentTypeRestrictedFileField, self).to_python(data)
        if f is None:
            return None

        if f.size > self.max_upload_size:
            raise ValidationError(self.error_messages['max_size'].format(
                filesizeformat(self.max_upload_size),
                filesizeformat(f.size)))

        content_type = magic.from_file(f.name, mime=True)
        if content_type not in self.content_types:
            raise ValidationError(self.error_messages['filetype'])

        return f

add_introspection_rules([], [
    "^swingers\.models\.fields\.ContentTypeRestrictedFileField"]
)
