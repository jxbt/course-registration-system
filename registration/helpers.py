import requests
import json
import random
import string
from django.utils import timezone
from .models import TwoFactorCode
import os

def admin_check(user):
    return user.is_superuser

def send_mail(recipient_email, subject, msg):
    api_key = os.getenv('MAILJET_API_KEY')
    api_secret = os.getenv('MAILJET_API_SECRET')
    
    post_data = {
        'Messages': [
            {
                'From': {
                    'Email': os.getenv('APP_SENDER_EMAIL'),
                    'Name': "Course service"
                },
                'To': [
                    {
                        'Email': recipient_email
                    }
                ],
                'Subject': subject,
                'TextPart': msg
            }
        ]
    }
    
    url = 'https://api.mailjet.com/v3.1/send'
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, auth=(api_key, api_secret), headers=headers, data=json.dumps(post_data))
    
    return response.json()


def generate_2fa_code():
    return ''.join(random.choices(string.digits, k=6))

def send_2fa_code(user):
    code = generate_2fa_code()
    expiration_time = timezone.now() + timezone.timedelta(minutes=10)
    TwoFactorCode.objects.create(user=user, code=code, expiration_time=expiration_time)
    send_mail(
        user.email,
        '2FA Code',
        f'Your 2FA code is {code}. It will expire in 10 minutes.'
    )