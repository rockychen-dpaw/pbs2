import logging
import datetime
import os
from functools import reduce

from django.contrib.gis.db import models
from django.utils import timezone
from django.db.models import Q,Max
from django.dispatch import receiver
from django.db.models.signals import post_delete

from dpaw_utils.models import (AuditMixin,ModelDictMixin)

from pbs.document.fields import ContentTypeRestrictedFileField
from pbs.document.utils import get_dimensions
from pbs.prescription.models import Prescription

logger = logging.getLogger(__name__)
# Create your models here.

def content_file_name(self, filename):
    if filename.rsplit('.')[-1] == "zip":
        extension = "zip"
    else:
        extension = "pdf"
    return "uploads/{0}/{0}_{1}_{2}_{3}.{4}".format(
        str(self.prescription.season).strip().replace("/", "_"),
        self.prescription.burn_id,
        self.descriptor.strip().replace(" ", "_"),
        timezone.localtime(self.document_created).isoformat(
        ).rsplit(".")[0].replace(":", "")[:-7],
        extension)


class DocumentCategory(models.Model):
    name = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Document Category"
        verbose_name_plural = "Document Categories"
        ordering = ['name']

class CategoryManager(models.Manager):
    def _query_by_names(self, *names):
        return reduce(lambda x, y: x | y,
                      (Q(name__iexact=name) for name in names),
                      Q())

    def not_tag_names(self, *names):
        return self.get_queryset().exclude(self._query_by_names(*names))

    def tag_names(self, *names):
        return self.get_queryset().filter(self._query_by_names(*names))


class DocumentTag(models.Model):
    name = models.CharField(verbose_name="Document Tag", max_length=200)
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT)

    objects = CategoryManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        base_manager_name = "objects"

class TagManager(models.Manager):
    def _query_by_names(self, *names):
        return reduce(lambda x, y: x | y,
                      (Q(tag__name__iexact=name) for name in names),
                      Q())

    def not_tag_names(self, *names):
        return self.get_queryset().exclude(self._query_by_names(*names))

    def tag_names(self, *names):
        return self.get_queryset().filter(self._query_by_names(*names))

    def __getattr__(self, name):
        if name[:4] == "tag_":
            qs = self.get_queryset().filter(
                tag__name__iexact=name[4:].replace("_", " "))
            qs.modified = qs.aggregate(Max('modified'))["modified__max"]
            return qs
        else:
            return super(TagManager, self).__getattr__(name)

    def printable(self):
        """
        Return the set of printable documents. This removes any zip files from
        the set of documents.
        """
        qs = self.get_queryset()
        return filter(lambda x: x.filename.endswith('.pdf'), qs)


class Document(ModelDictMixin,AuditMixin):
    prescription = models.ForeignKey(
        Prescription, null=True,
        help_text="Prescription that this document belongs to", on_delete=models.PROTECT)
    category = models.ForeignKey(DocumentCategory, related_name="documents", on_delete=models.PROTECT)
    tag = models.ForeignKey(DocumentTag, verbose_name="Descriptor", on_delete=models.PROTECT)
    custom_tag = models.CharField(
        max_length=64, blank=True, verbose_name="Custom Descriptor")
    document = ContentTypeRestrictedFileField(
        upload_to=content_file_name, max_length=200,
        content_types=['application/pdf', 'image/tiff', 'image/tif',
                       'image/jpeg', 'image/jpg', 'image/gif', 'image/png',
                       'application/zip', 'application/x-zip-compressed'],
        help_text='Acceptable file types: pdf, tiff, jpg, gif, png, zip')

    document_created = models.DateTimeField(
        verbose_name="Date Document Created", default=timezone.now, editable=True, null=True, blank=True)

    document_archived = models.BooleanField(default=False, verbose_name="Archived Document")

    objects = TagManager()

    @property
    def descriptor(self):
        if self.custom_tag:
            return "Other ({0})".format(self.custom_tag)
        else:
            return self.tag.name

    @property
    def dimensions(self):
        return get_dimensions(self.document.path)

    @property
    def filename(self):
        try:
            return os.path.basename(self.document.path)
        except:
            return None

    @property
    def exists(self):
        """
        Check if file exists on the file system
        """
        try:
            return os.path.exists(self.document.file.name)
        except:
            return False


    @property
    def is_zipped(self):
        return self.filename.endswith('.zip')

    def clean(self):
        if not self.pk:
            self.category = self.tag.category

    def save(self, *args, **kwargs):
        super(Document, self).save(*args, **kwargs)
        # confirm that file is written to filesystem, if not remove the record
        if not self.exists:
            fname = self.document.name
            Document.objects.get(id=self.id).delete()
            raise Exception('ERROR: File not created on filesystem {}'.format(fname))
        return

    def __str__(self):
        return "{0} - {1}".format(self.prescription, self.document.name)

    class Meta:
        base_manager_name = "objects"
        ordering = ['tag', 'document']
        permissions = (
            ("archive_document", "Can archive documents")
        ,)

class DocumentListener(object):
    @staticmethod
    @receiver(post_delete, sender=Document)
    def delete_document(sender, instance, **kwargs):
        if instance.document:
            instance.document.delete(False)
