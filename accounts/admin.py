from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User
from django.utils.translation import gettext_lazy as _

admin.site.site_title = _("भण्डारण Admin Site")
admin.site.site_header = _("भण्डारण Admin")

class UserAdmin(BaseUserAdmin):
    list_display = ("email", "display_name", "username", "is_admin", "is_active")
    list_filter = ("is_admin", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("display_name", "username",)}),
        (
            "Permissions",
            {"fields": ("is_admin", "is_active", "is_staff", "is_superuser")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "display_name", "username", "password1", "password2", "is_admin"),
            },
        ),
    )

    search_fields = ("email", "display_name", "username",)
    ordering = ("id",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.unregister(Group)