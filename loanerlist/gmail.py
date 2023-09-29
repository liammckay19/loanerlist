# gmail.py

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

def get_service():
    # creds = None
    # # The file token.pickle stores the user's access and refresh tokens, and is
    # # created automatically when the authorization flow completes for the first
    # # time.
    # if os.path.exists('token.pickle'):
    #     with open('token.pickle', 'rb') as token:
    #         creds = pickle.load(token)
    # # If there are no (valid) credentials available, let the user log in.
    # if not creds:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         from google_auth_oauthlib.flow import Flow

    #         # Create the flow using the client secrets file from the Google API
    #         # Console.
    #         flow = Flow.from_client_secrets_file(
    #             os.path.join(BASE_DIR,'client_secret.json'),
    #             scopes=['https://www.googleapis.com/auth/gmail.compose'],
    #             redirect_uri='https://www.getagig.app')

    #         # Tell the user to go to the authorization URL.
    #         auth_url, _ = flow.authorization_url(prompt='consent')

    #         print('Please go to this URL: {}'.format(auth_url))

    #         # The user will get an authorization code. This code is used to get the
    #         # access token.
    #         code = input('Enter the authorization code: ')
    #         flow.fetch_token(code=code)

    #         # Update the creds variable
    #         creds = flow.credentials

    #         # You can use flow.credentials, or you can just get a requests session
    #         # using flow.authorized_session.
    #         session = flow.authorized_session()
    #         print(session.get('https://www.googleapis.com/userinfo/v2/me').json())

    #         # Save the updated credentials for the next run
    #         with open('token.pickle', 'wb') as token:
    #             pickle.dump(creds, token)

    #             # Save the credentials for the next run
    #             with open('token.pickle', 'wb') as token:
    #                 pickle.dump(creds, token)

    # service = build('gmail', 'v1', credentials=creds)

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


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id,
                body=message).execute()

        print('Message Id: {}'.format(message['id']))

        return message
    except Exception as e:
        print('An error occurred: {}'.format(e))
        return None

def create_message_with_attachment(
    sender,
    to,
    subject,
    message_text,
):
    # Create the email body
    unsubscribe_link = "https://www.getagig.app/settings/account/"
    unsubscribe_text = "Unsubscribe"

    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(f"{message_text}\n\nTo unsubscribe, click here: <a href='{unsubscribe_link}'>{unsubscribe_text}</a>. Unckeck the checkbox for \"Allow email communication from artists/talent buyers on Getagig\"", "html")
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
    return {'raw': raw_message.decode('utf-8')}

def sendingMessage(email_from, email_to,subject,message):
    service = get_service()
    user_id = 'me'
    msg = create_message_with_attachment(email_from, email_to, subject, message)
    send_message(service, user_id, msg)

    # from django.core.mail import send_mail
    # if "," in email_to:
    #     email_to = email_to.split(",")
    # else:
    #     email_to = [email_to]
    # send_mail(
    #     subject,
    #     message,
    #     email_from,
    #     email_to,
    #     fail_silently=False,
    # )