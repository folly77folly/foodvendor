from django.core.mail import send_mail
import random, string, datetime
from decouple import config




def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

def sendmail(request, reference_id, subject):
    data = request.data
    to_email = [data['email']]
    base_url =  config("BASE_URL")
    set_password_url = config("SET_PASSWORD_URL", default="api/v.1/auth/setpassword/")
    rest_link = f'<a href="{base_url+set_password_url+reference_id}">Set password</a>'
    SENDER = config("EMAIL_HOST_USER", default="ppmogunstatealerts@gmail.com")
    from_email = SENDER
    html_content = f"Click on the link below to set your password\n{rest_link}"
    send_mail(subject, html_content , from_email, to_email, fail_silently=False,)