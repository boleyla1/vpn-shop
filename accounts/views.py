from datetime import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import uuid

from .models import User, Otp
from .forms import PhoneLoginForm, RegisterForm, VerifyOtpForm
from .utils import send_otp_sms, generate_otp_code


class LoginRegisterView(View):
    """نمایش صفحه ورود/ثبت‌نام"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:index')

        return render(request, 'accounts/login.html')


class SendOtpView(View):
    """ارسال کد OTP (پاسخ JSON)"""

    def post(self, request):
        form_type = request.POST.get('form_type')

        if form_type == 'login':
            form = PhoneLoginForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone']

                # بررسی وجود کاربر
                if not User.objects.filter(phone=phone).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'کاربری با این شماره یافت نشد. لطفاً ثبت‌نام کنید.'
                    })

                # تولید توکن و کد
                token = str(uuid.uuid4())
                code = generate_otp_code()

                # حذف OTP های قبلی این شماره
                Otp.objects.filter(phone=phone).delete()

                # ذخیره OTP جدید
                Otp.objects.create(token=token, phone=phone, code=code)

                # ارسال پیامک
                send_otp_sms(phone, code)

                return JsonResponse({
                    'success': True,
                    'token': token,
                    'message': 'کد تایید ارسال شد'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'شماره موبایل نامعتبر است'
                })

        elif form_type == 'register':
            form = RegisterForm(request.POST)
            if form.is_valid():
                phone = form.cleaned_data['phone']

                # بررسی تکراری نبودن
                if User.objects.filter(phone=phone).exists():
                    return JsonResponse({
                        'success': False,
                        'message': 'این شماره قبلاً ثبت شده است. لطفاً وارد شوید.'
                    })

                # تولید توکن و کد
                token = str(uuid.uuid4())
                code = generate_otp_code()

                # حذف OTP های قبلی
                Otp.objects.filter(phone=phone).delete()

                # ذخیره OTP
                Otp.objects.create(token=token, phone=phone, code=code)

                # ذخیره اطلاعات در session (موقت)
                request.session['register_data'] = {
                    'first_name': form.cleaned_data['first_name'],
                    'last_name': form.cleaned_data['last_name'],
                    'phone': phone,
                }

                # ارسال پیامک
                send_otp_sms(phone, code)

                return JsonResponse({
                    'success': True,
                    'token': token,
                    'message': 'کد تایید ارسال شد'
                })
            else:
                errors = form.errors.as_json()
                return JsonResponse({
                    'success': False,
                    'message': 'اطلاعات وارد شده معتبر نیست',
                    'errors': errors
                })

        return JsonResponse({
            'success': False,
            'message': 'درخواست نامعتبر'
        })


class VerifyOtpView(View):
    """تایید کد OTP (پاسخ JSON)"""

    def post(self, request):
        token = request.POST.get('token')
        code = request.POST.get('code')

        if not token or not code:
            return JsonResponse({
                'success': False,
                'message': 'توکن یا کد ارسال نشده است'
            })

        try:
            otp = Otp.objects.get(token=token, code=code)

            # بررسی انقضا
            if otp.is_expired():
                otp.delete()
                return JsonResponse({
                    'success': False,
                    'message': 'کد منقضی شده است. لطفاً دوباره درخواست دهید.'
                })

            phone = otp.phone

            # بررسی ثبت‌نام یا ورود
            user = User.objects.filter(phone=phone).first()

            if user:
                # ورود
                login(request, user)
                otp.delete()
                return JsonResponse({
                    'success': True,
                    'message': 'ورود موفقیت‌آمیز',
                    'redirect_url': '/'
                })
            else:
                # ثبت‌نام
                register_data = request.session.get('register_data')

                if not register_data or register_data['phone'] != phone:
                    return JsonResponse({
                        'success': False,
                        'message': 'اطلاعات ثبت‌نام یافت نشد. لطفاً دوباره تلاش کنید.'
                    })

                # ایجاد کاربر جدید
                user = User.objects.create_user(
                    phone=phone,
                    first_name=register_data['first_name'],
                    last_name=register_data['last_name']
                )

                # پاک کردن session
                del request.session['register_data']

                # ورود خودکار
                login(request, user)
                otp.delete()

                return JsonResponse({
                    'success': True,
                    'message': 'ثبت‌نام و ورود موفقیت‌آمیز',
                    'redirect_url': '/'
                })

        except Otp.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'کد وارد شده صحیح نیست'
            })


class ResendOtpView(View):
    """ارسال مجدد کد OTP"""

    def post(self, request):
        token = request.POST.get('token')

        if not token:
            return JsonResponse({
                'success': False,
                'message': 'توکن ارسال نشده است'
            })

        try:
            # پیدا کردن OTP قبلی
            old_otp = Otp.objects.get(token=token)
            phone = old_otp.phone

            # تولید کد جدید
            new_code = generate_otp_code()

            # به‌روزرسانی کد و زمان
            old_otp.code = new_code
            old_otp.created_at = timezone.now()
            old_otp.save()

            # ارسال پیامک
            send_otp_sms(phone, new_code)

            return JsonResponse({
                'success': True,
                'message': 'کد جدید ارسال شد'
            })

        except Otp.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'توکن نامعتبر است'
            })


class LogoutView(View):
    """خروج کاربر"""

    def get(self, request):
        logout(request)
        messages.success(request, 'با موفقیت خارج شدید.')
        return redirect('core:index')
