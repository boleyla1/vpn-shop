from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Otp


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """پنل مدیریت کاربران"""

    list_display = ('phone', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('phone', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('اطلاعات شخصی', {'fields': ('first_name', 'last_name')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('تاریخ‌ها', {'fields': ('date_joined',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'first_name', 'last_name'),
        }),
    )

    readonly_fields = ('date_joined',)


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    """پنل مدیریت کدهای تایید"""

    list_display = ('phone', 'code', 'token', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('phone', 'code')
    readonly_fields = ('token', 'created_at')
    ordering = ('-created_at',)
