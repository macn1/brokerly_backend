from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Domain
from django.utils.translation import gettext_lazy as _

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    ordering = ("id",)
    list_display = ("email", "name", "role", "phone_number", "is_active", "is_staff")
    search_fields = ("email", "name", "phone_number")
    list_filter = ("role", "is_active", "is_staff")

    # fields shown on user change page in admin
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("name", "phone_number", "role", "domain")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")
