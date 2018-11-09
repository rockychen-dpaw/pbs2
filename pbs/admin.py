from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin, GroupAdmin


from pbs.forms import (UserForm, )
# Register your models here.

class UserAdmin(AuthUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_active')
    actions = None
    form = UserForm
    fieldsets = (
        (None, {'fields': ('username', 'email', ('first_name', 'last_name'),
                           'is_active', 'groups')}),
    )
    list_filter = ("is_active", "groups")

#admin.site.register(User, UserAdmin)
#admin.site.register(Group, GroupAdmin)

