import os

from django.conf import settings
from pbs.document.models import Document


def create_fake_missing_documents():
    documents = Document.objects.all()
    for doc in documents:
        if os.path.exists(doc.document.path):
            continue
        path,filename = os.path.split(doc.document.path)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(doc.document.path,"w") as f:
            pass
        break



