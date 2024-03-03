from django.shortcuts import render
import os
from django import forms
from . import forms
from django.http import HttpResponseRedirect
# from django.core.mail import send_mail
from .secrets import user, passwd
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from .settings import BASE_DIR

from django.http import HttpResponse


def index(request):
    path = "ebdjango/static"
    img_list = []
    for f in os.listdir(path):
        if f.endswith("jpg") or f.endswith("png"):
            img_list.append(f)
    return render(request, 'ecard/index.html', {'images': img_list})


def send_mail(send_from, send_to, subject, message, files=[],
              server="mail.atourcity.com", port=587, username=user, password=passwd,
              use_tls=False):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (str): to name
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(os.path.basename(path)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()


def detail(request):
    try:
        ecard = request.POST['ecard']
    except (KeyError):
        return index(request)
    else:
        form = forms.ContactForm()
        return render(request, 'ecard/detail.html', {'ecard': ecard, 'form': form})


def thankyou(request):
    form = forms.ContactForm(request.POST)
    ecard = request.POST['ecard']
    ecard_path = os.path.join(BASE_DIR, "ebdjango/static/", ecard)
    if form.is_valid():
        recipients = [form.cleaned_data['receiver'],]
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        sender = form.cleaned_data['sender']
        cc_myself = form.cleaned_data['cc_myself']

        if cc_myself:
            recipients.append(sender)

        message = message + "      From: " + sender
        send_mail(user, recipients, subject, message, [ecard_path, ])
        return HttpResponseRedirect('thanks/')
    else:
        form = forms.ContactForm()
        return render(request, 'ecard/detail.html', {'ecard': ecard, 'form': form})


def thanks(request):
    return HttpResponse("<H1>Thank You!</H1>")
