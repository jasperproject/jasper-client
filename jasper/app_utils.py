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

    body = 'Hello %s,' % config['first_name']
    body += '\n\n' + BODY.strip() + '\n\n'
    body += 'Best Regards,\nJasper\n'

    recipient = None

    if config['prefers_email']:
        if config['gmail_address']:
            recipient = config['gmail_address']
            if config['first_name'] and config['last_name']:
                recipient = "%s %s <%s>" % (
                    config['first_name'],
                    config['last_name'],
                    recipient)
    else:
        if config['carrier'] and config['phone_number']:
            recipient = "%s@%s" % (
                str(config['phone_number']),
                config['carrier'])

    if not recipient:
        return False

    try:
        if 'mailgun' in config:
            user = config['mailgun']['username']
            password = config['mailgun']['password']
            server = 'smtp.mailgun.org'
        else:
            user = config['gmail_address']
            password = config['gmail_password']
            server = 'smtp.gmail.com'
        send_email(SUBJECT, body, recipient, user,
                   "Jasper <jasper>", password, server)

    except Exception:
        return False
    else:
        return True


def get_timezone(config):
    """
    Returns the pytz timezone for a given config.

    Arguments:
        config -- contains information related to the user (e.g., email
                   address)
    """
    try:
        return timezone(config['timezone'])
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
