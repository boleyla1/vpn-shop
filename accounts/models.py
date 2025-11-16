from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """مدیریت کاربران سفارشی"""

    def create_user(self, phone, first_name='', last_name='', password=None, **extra_fields):
        """ایجاد کاربر عادی"""
        if not phone:
            raise ValueError('شماره موبایل الزامی است')

        user = self.model(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        """ایجاد سوپریوزر"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """مدل کاربر سفارشی با شماره موبایل"""

    phone = models.CharField('شماره موبایل', max_length=11, unique=True)
    first_name = models.CharField('نام', max_length=50, blank=True)
    last_name = models.CharField('نام خانوادگی', max_length=50, blank=True)

    is_active = models.BooleanField('فعال', default=True)
    is_staff = models.BooleanField('کارمند', default=False)
    is_superuser = models.BooleanField('ادمین', default=False)

    date_joined = models.DateTimeField('تاریخ عضویت', default=timezone.now)

    # اضافه کردن related_name برای جلوگیری از Clash
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='گروه‌ها',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='دسترسی‌ها',
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.phone

    def get_full_name(self):
        """بازگرداندن نام کامل"""
        return f"{self.first_name} {self.last_name}".strip() or self.phone

    def get_short_name(self):
        """بازگرداندن نام کوتاه"""
        return self.first_name or self.phone


class Otp(models.Model):
    """مدل کد یکبار مصرف"""

    token = models.UUIDField('توکن', unique=True)
    phone = models.CharField('شماره موبایل', max_length=11)
    code = models.CharField('کد تایید', max_length=4)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'کد تایید'
        verbose_name_plural = 'کدهای تایید'

    def __str__(self):
        return f"{self.phone} - {self.code}"

    def is_expired(self):
        """بررسی انقضای کد (3 دقیقه)"""
        return (timezone.now() - self.created_at).total_seconds() > 180
