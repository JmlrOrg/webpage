"""
Usage: python bin/send_emails.py vol id1  id2  id3
Example: python bin/send_emails.py 19 16-210  16-656
will process papers with id 16-210 and 16-656 from volume 19

First make sure you have credentials set up
https://developers.google.com/workspace/guides/create-credentials

"""

import sys
import os
import json
import pickle
import time
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from email.mime.text import MIMEText
import base64

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_emails(vol, id):
    print('Processing paper ID %s' % id)

    with open('v%s/%s/info.json' % (vol, id), 'r') as fp:
        # some cleanup for the html display
        info = json.load(fp)

    emails = info['emails']
    recipients = [e.strip('\n') for e in emails]

    msg = \
"""Dear Authors,\n
Your JMLR submission %s, "%s", in now online. It can be found at http://jmlr.org/papers/v%s/%s.html. Please take a moment to check the author order, abstract, and bibtex. We are now using UTF encoded bibtex files that can be interpreted using LaTeX's inputenc package.\n\nFurthermore, we would like to know about your experience publishing with JMLR. This feedback will allow us to improve and provide a better service. Please take a minute to fill the following survey:\n
    https://docs.google.com/forms/d/e/1FAIpQLSftyqPSdmiiKyoCuFRNPjZRlYQrTXPEx8SU0CaQJ3XQS9LJCg/viewform\n
We thank you for publishing your research with JMLR.\n
Fabian Pedregosa and Alp Kucukelbir (JMLR Webmasters)\non behalf of the JMLR editorial board.
""" % (id, info['title'], vol, id)

    message = create_message(
        sender='Alp Kucukelbir <alp@jmlr.org>',
        to=",".join(recipients),
        subject=f"JMLR submission {id} is now online",
        message_text=msg)

    send_message(service, 'me', message)

    print('Email sent to', ", ".join(recipients))

    time.sleep(0.5)


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
    b64_string = b64_bytes.decode()

    return {'raw': b64_string}


def send_message(service, user_id, message):
    try:
        message = (service.users().messages()
                   .send(userId=user_id, body=message)
                   .execute())
        return message
    except HttpError as e:
        print(f'An error occurred: {e}')


if __name__ == '__main__':
    vol = sys.argv[1]
    ids = sys.argv[2:]

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    for id in ids:
        send_emails(vol, id)
        print()
