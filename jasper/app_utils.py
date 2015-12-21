# -*- coding: utf-8 -*-
import smtplib
from email.MIMEText import MIMEText
import urllib2
import re
from pytz import timezone


def send_email(SUBJECT, BODY, TO, FROM, SENDER, PASSWORD, SMTP_SERVER):
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


def email_user(config, SUBJECT="", BODY=""):
    """
    sends an email.

    Arguments:
        config -- contains information related to the user (e.g., email
                   address)
        SUBJECT -- subject line of the email
        BODY -- body text of the email
    """
    if not BODY:
        return False

    body = 'Hello %s,' % config.get('first_name')
    body += '\n\n' + BODY.strip() + '\n\n'
    body += 'Best Regards,\nJasper\n'

    recipient = None

    if config.get('prefers_email'):
        if config.get('gmail_address'):
            recipient = config.get('gmail_address')
            if config.get('first_name') and config('last_name'):
                recipient = "%s %s <%s>" % (
                    config.get('first_name'),
                    config.get('last_name'),
                    recipient)
    else:
        if config.get('carrier') and config('phone_number'):
            recipient = "%s@%s" % (
                str(config.get('phone_number')),
                config.get('carrier'))

    if not recipient:
        return False

    user = config.get('mailgun', 'username')
    password = config.get('mailgun', 'password')
    server = 'smtp.mailgun.org'

    if not all(user, password, server):
        user = config.get('gmail_address')
        password = config.get('gmail_password')
        server = 'smtp.gmail.com'

    if all(user, password, server):
        try:
            send_email(SUBJECT, body, recipient, user,
                       "Jasper <jasper>", password, server)
        except Exception:
            pass
        else:
            return True

    return False


def get_timezone(config):
    """
    Returns the pytz timezone for a given config.

    Arguments:
        config -- contains information related to the user (e.g., email
                   address)
    """
    try:
        return timezone(config.get('timezone'))
    except:
        return None


def generate_tiny_URL(URL):
    """
    Generates a compressed URL.

    Arguments:
        URL -- the original URL to-be compressed
    """
    target = "http://tinyurl.com/api-create.php?url=" + URL
    response = urllib2.urlopen(target)
    return response.read()


def is_negative(phrase):
    """
    Returns True if the input phrase has a negative sentiment.

    Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(no(t)?|don\'t|stop|end|n)\b', phrase,
                          re.IGNORECASE))


def is_positive(phrase):
    """
        Returns True if the input phrase has a positive sentiment.

        Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return bool(re.search(r'\b(sure|yes|yeah|go|yup|y)\b',
                          phrase,
                          re.IGNORECASE))
