# -*- coding: utf-8-*-
import os
import smtplib
from email.MIMEText import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import urllib2
import re
from pytz import timezone


def sendEmail(SUBJECT, BODY, TO, FROM, SENDER, PASSWORD, SMTP_SERVER):
    """Sends an HTML email."""
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            BODY.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
    msg = MIMEText(BODY.encode(body_charset), 'html', body_charset)
    msg['From'] = SENDER
    msg['To'] = TO
    msg['Subject'] = SUBJECT

    SMTP_PORT = 587
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.starttls()
    session.login(FROM, PASSWORD)
    session.sendmail(SENDER, TO, msg.as_string())
    session.quit()


def sendImageEmail(SUBJECT, BODY, TO, FROM, SENDER, PASSWORD, SMTP_SERVER,
                   IMAGE_FILE):
    """Sends an HTML email and an image attachment"""
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            BODY.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break
    imageData = open(IMAGE_FILE, 'rb').read()
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    emailText = MIMEText(BODY.encode(body_charset), 'html', body_charset)
    msg.attach(emailText)
    emailImage = MIMEImage(imageData, name=os.path.basename(IMAGE_FILE))
    msg.attach(emailImage)

    SMTP_PORT = 587
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    session.starttls()
    session.login(FROM, PASSWORD)
    session.sendmail(SENDER, TO, msg.as_string())
    session.quit()


def emailUser(profile, SUBJECT="", BODY="", imageFile=None):
    """
    sends an email.

    Arguments:
        profile -- contains information related to the user (e.g., email
                   address)
        SUBJECT -- subject line of the email
        BODY -- body text of the email
    """
    def generateSMSEmail(profile):
        """
        Generates an email from a user's phone number based on their carrier.
        """
        if profile['carrier'] is None or not profile['phone_number']:
            return None

        return str(profile['phone_number']) + "@" + profile['carrier']

    if profile['prefers_email'] and profile['gmail_address']:
        # add footer
        if BODY:
            BODY = profile['first_name'] + \
                ",<br><br>Here are your top headlines:" + BODY
            BODY += "<br>Sent from your Jasper"

        recipient = profile['gmail_address']
        if profile['first_name'] and profile['last_name']:
            recipient = profile['first_name'] + " " + \
                profile['last_name'] + " <%s>" % recipient
    else:
        recipient = generateSMSEmail(profile)

    if not recipient:
        return False

    try:
        if 'mailgun' in profile:
            user = profile['mailgun']['username']
            password = profile['mailgun']['password']
            server = 'smtp.mailgun.org'
        else:
            user = profile['gmail_address']
            password = profile['gmail_password']
            server = 'smtp.gmail.com'
        if imageFile is None:
            sendEmail(SUBJECT, BODY, recipient, user,
                  "Jasper <jasper>", password, server)
        else:
            sendImageEmail(SUBJECT, BODY, recipient, user,
                  "Jasper <jasper>", password, server, imageFile)

        return True
    except:
        return False


def getTimezone(profile):
    """
    Returns the pytz timezone for a given profile.

    Arguments:
        profile -- contains information related to the user (e.g., email
                   address)
    """
    try:
        return timezone(profile['timezone'])
    except:
        return None


def generateTinyURL(URL):
    """
    Generates a compressed URL.

    Arguments:
        URL -- the original URL to-be compressed
    """
    target = "http://tinyurl.com/api-create.php?url=" + URL
    response = urllib2.urlopen(target)
    return response.read()


def isNegative(phrase):
    """
    Returns True if the input phrase has a negative sentiment.

    Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(no(t)?|don\'t|stop|end)\b', phrase,
                          re.IGNORECASE))


def isPositive(phrase):
    """
        Returns True if the input phrase has a positive sentiment.

        Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(sure|yes|yeah|go)\b', phrase, re.IGNORECASE))
