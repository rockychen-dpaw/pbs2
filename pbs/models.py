import logging

from django.contrib.auth.models import User, Group
from django.contrib.gis.db import models
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from pbs.prescription.models import Region, District

logger = logging.getLogger("log." + __name__)
# Create your models here.
class Profile(models.Model):
    DEFAULT_GROUP = "Users"
    
    TABLE_EXISTS = False

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.PROTECT)
    district = models.ForeignKey(District,blank=True,null=True,on_delete=models.PROTECT)

    @property
    def is_fpc_user(self):
        return self.user.email.lower().endswith(settings.FPC_EMAIL_EXT)

Profile.TABLE_EXISTS = Profile()._meta.db_table in connection.introspection.table_names()

@receiver(post_save,sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Create a user profile when a new user account is created"""
    if created and Profile.TABLE_EXISTS:
        p = Profile()
        p.user = instance
        p.save()

        # add the default user group (fail_silently=True)
        try:
            group = Group.objects.get(name__iexact=p.DEFAULT_GROUP)
        except Group.DoesNotExist:
            logger.warning("Failed to assign group `%s' to user `%s', "
                           "group `%s' does not exist.", p.DEFAULT_GROUP,
                           p.user.username, p.DEFAULT_GROUP)
        else:
            p.user.groups.add(group)

