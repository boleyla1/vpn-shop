# accounts/utils.py

import requests
import json
from django.conf import settings
from random import randint


def send_otp_sms(phone, code):
    """ارسال کد OTP از طریق API قاصدک"""

    url = "https://gateway.ghasedak.me/rest/api/v1/WebService/SendOtpWithParams"

    payload = json.dumps({
        "receptors": [
            {
                "mobile": str(phone),
                "clientReferenceId": "1"
            }
        ],
        "templateName": "boleyla",  # نام تمپلیت خودت رو بذار
        "param1": str(code),
        "lineNumber": "30005006004099",  # خط خودت رو بذار
        "isVoice": False,
        "udh": False,
    })

    headers = {
        'Content-Type': 'application/json',
        'ApiKey': settings.GHASEDAK_API_KEY
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        print(f"SMS sent to {phone}: {code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return False


def generate_otp_code():
    """تولید کد 4 رقمی تصادفی"""
    return randint(1000, 9999)
