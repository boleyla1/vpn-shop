# accounts/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from datetime import timedelta
from .models import Otp, User
import re


class PhoneLoginForm(forms.Form):
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3',
            'placeholder': '9123456789',
            'maxlength': '10',
            'id': 'loginPhone'
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        # بررسی طول شماره
        if len(phone) != 10:
            raise ValidationError('شماره تلفن باید 10 رقم باشد.')

        # بررسی شروع با 9
        if not phone.startswith('9'):
            raise ValidationError('شماره تلفن باید با 9 شروع شود.')

        # بررسی عدد بودن
        if not phone.isdigit():
            raise ValidationError('شماره تلفن فقط باید شامل اعداد باشد.')

        return '0' + phone  # اضافه کردن 0 به ابتدا


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3',
            'placeholder': 'نام خود را وارد کنید'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3',
            'placeholder': 'نام خانوادگی خود را وارد کنید'
        })
    )
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3',
            'placeholder': '9123456789',
            'maxlength': '10',
            'id': 'registerPhone'
        })
    )
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'لطفاً قوانین و مقررات را بپذیرید.'}
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if len(phone) != 10:
            raise ValidationError('شماره تلفن باید 10 رقم باشد.')

        if not phone.startswith('9'):
            raise ValidationError('شماره تلفن باید با 9 شروع شود.')

        if not phone.isdigit():
            raise ValidationError('شماره تلفن فقط باید شامل اعداد باشد.')

        return '0' + phone


class VerifyOtpForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=4,
        widget=forms.TextInput(attrs={
            'class': 'w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-center text-2xl tracking-widest',
            'placeholder': '______',
            'maxlength': '6'
        })
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']

        if not code.isdigit():
            raise ValidationError('کد فقط باید شامل اعداد باشد.')

        if not self.token:
            raise ValidationError('توکن معتبر نیست!')

        try:
            otp = Otp.objects.get(code=code, token=self.token)
            if otp.is_expired():
                otp.delete()
                raise ValidationError('کد منقضی شده است. لطفاً دوباره درخواست دهید.')
        except Otp.DoesNotExist:
            raise ValidationError('کد وارد شده معتبر نیست.')

        return code
