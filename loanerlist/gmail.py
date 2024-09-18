# gmail.py
# gmail account avidexloanerlist@gmail.com - password is k@FOi!z2&oX&EFok

import smtplib
import ssl
from email.message import EmailMessage

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_service():
    # creds = None
    # if os.path.exists('token.pickle'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)

    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             os.path.join(BASE_DIR, 'client_secret.json'), SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     with open('token.pickle', 'wb') as token:
    #         pickle.dump(creds, token)

    # service = build('gmail', 'v1', credentials=creds)
    # return service

    # SERVICE ACCOUNT -- GMAIL API "getagig"
    # https://console.cloud.google.com/iam-admin/serviceaccounts/details/118415158185647241324;edit=true/keys?project=getagig-379702
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

    # Load the service account JSON key file
    credentials = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR,'client_secret.json'), scopes=SCOPES)
    delegated_credentials = credentials.with_subject('getagig@stickdrum.org')


    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=delegated_credentials)

    return service


import traceback

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: {}'.format(message['id']))
        return message
    except Exception as e:
        print('An error occurred:', e)
        traceback.print_exc()  # Print detailed error
        return None


def create_message_with_attachment(
    sender,
    to,
    subject,
    message_text,
):
    # Create the email body
    unsubscribe_link = "https://avidexloanerlistfremont.pythonanywhere.com/login"
    unsubscribe_text = "Login"

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(f"{message_text}\n\n<a href='{unsubscribe_link}'>{unsubscribe_text}</a>.", "html")
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
    return {'raw': raw_message.decode('utf-8')}

def sendingMessage(email_from, email_to,subject,message):

    # Step 1: Enable 2-factor authentication at account.google.com

    # Step 2: Go to the app passwords page and generate a password
    # Go to: https://myaccount.google.com/u/4/apppasswords
    # Select App: Choose "Other" and type in a name, e.g., Python
    # Click "Generate" to get the app password, which you'll use in your script

    # Example Python Email Script using the app password

    smtp_server = "smtp.gmail.com"
    port = 465  # For SSL

    sender_email = "avidexloanerlist@gmail.com"  # The Gmail account the password was generated for
    receiver_email = email_to  # The receiver's email address
    password = "mfqh qcsb xksq ycjt"  # The password generated via the app passwords

    subject = "Python Email"
    body = message

    # Create email message
    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content(body)

    # Create a secure SSL context and send the email
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, em.as_string())

    # Email should now be sent

    # service = get_service()
    # user_id = 'liammckay2019@gmail.com'
    # msg = create_message_with_attachment(email_from, email_to, subject, message)
    # send_message(service, user_id, msg)

    # # from django.core.mail import send_mail
    # # if "," in email_to:
    # #     email_to = email_to.split(",")
    # # else:
    # #     email_to = [email_to]
    # # send_mail(
    # #     subject,
    # #     message,
    # #     email_from,
    # #     email_to,
    # #     fail_silently=False,
    # # )