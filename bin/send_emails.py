"""
Usage: python bin/send_emails.py vol id1  id2  id3

Example: python bin/send_emails.py 19 16-210  16-656
will process papers with id 16-210 and 16-656 from volume 19
"""

import sys
import os
import json

def send_emails(vol, id):
    print('Processing paper ID %s' % id)

    with open('data/v%s/%s/info.json' % (vol, id), 'r') as fp:
        # some cleanup for the html display
        info = json.load(fp)

    from email.mime.text import MIMEText
    import smtplib
    if False:
        recipients = []
        recipients.append('webmaster@jmlr.org')
    else:
        with open('data/v%s/%s/.emails.txt' % (vol, id), 'r') as fp:
            emails = fp.readlines()
        recipients = [e.strip('\n') for e in emails]
        recipients.append('webmaster@jmlr.org')
        recipients.append('alp@jmlr.org')
    for rec in recipients:
        msg = MIMEText(
        """Dear Author,

your JMLR submission %s, "%s", in now online. It can be found at http://jmlr.org/papers/v%s/%s.html . Please take a moment to check the author order, abstract and bibtex. You can let us know of any desired changes by replying to this email.

We thank you for publishing your research with JMLR.

Fabian Pedregosa (JMLR Webmaster) on behalf of the JMLR editorial board.
        """ % (id, info['title'], vol, id))
        msg['Subject'] = "JMLR submission %s is now online" % id
        msg['From'] = 'JMLR Webmaster <f@bianp.net>'
        msg['To'] = rec
        username = os.environ['JMLR_SEND_EMAIL']
        password = os.environ['JMLR_SEND_EMAIL_PASS']
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username,password)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        print('Email sent', msg['To'])
        import time
        time.sleep(15)


if __name__ == '__main__':
    vol = sys.argv[1]
    ids = sys.argv[2:]
    for id in ids:
        send_emails(vol, id)
