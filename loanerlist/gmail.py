# gmail.py

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
import smtplib
import ssl
from email.message import EmailMessage
import json
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


def sendingMessage(email_from, email_to, subject, message):
    """
    Send an email using SendGrid SMTP with click tracking disabled.
    """

    # Create the email message
    em = EmailMessage()
    em['From'] = email_from
    em['To'] = email_to
    em['Subject'] = subject
    em.set_content(message, subtype='html')

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Use SMTP_SSL for a secure connection
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(username, password)
        server.sendmail(email_from, email_to, em.as_string())
    print("Email sent successfully!")
