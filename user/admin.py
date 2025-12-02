from django.contrib import admin
from user.models import Users
from django.contrib.auth.admin import UserAdmin 
from django.contrib.auth.models import Group 
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken
)
from unfold.admin import ModelAdmin
from user.forms import UserAdminForm

admin.site.unregister(Group)

@admin.register(Users)
class UserAdmin(ModelAdmin):
    form = UserAdminForm

    list_display = [
        field.name 
        for field in Users._meta.fields 
        if field.name not in ['username', 'first_name', 'last_name', 'password', 'is_superuser', 'last_login', 'is_staff', 'date_joined']
    ]

    search_fields = ('id', 'email', 'full_name', 'phone')
    list_filter = ('is_active', 'date_joined',)
    list_display_links = ('id', 'email', 'full_name', 'is_active')
    list_per_page = 20

    exclude = ('username', 'first_name', 'last_name', 'password', 'is_superuser', 'last_login', 'is_staff', 'groups', 'user_permissions', 'date_joined')

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        new_password = form.cleaned_data.get("new_password")
        if new_password:
            obj.set_password(new_password)
        obj.save()


admin.site.unregister(BlacklistedToken)
admin.site.unregister(OutstandingToken)

