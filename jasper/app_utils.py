# -*- coding: utf-8 -*-
import smtplib
from email.MIMEText import MIMEText
import urllib2
import re
from pytz import timezone

NEGATIVE = ["no", "nope", "not now", "deny", "don\'t", "stop", "end", "n"]
POSITIVE = ["yes", "yeah", "yup", "ok(ay)?", "al(l\s)?right(y)?",
                  "(sounds\s)?good", "check", "cool", "confirm",
                  "affirm", "sure", "go", "y"]
CANCEL = ["never(\s)?mind", "cancel"]
REPEAT = ["repeat", "again", "what was that"]

NEGATIVE = re.compile(r"\b(%s)\b" % "|".join(NEGATIVE), re.IGNORECASE)
POSITIVE = re.compile(r"\b(%s)\b" % "|".join(POSITIVE), re.IGNORECASE)
CANCEL = re.compile(r"\b(%s)\b" % "|".join(CANCEL), re.IGNORECASE)
REPEAT = re.compile(r"\b(%s)\b" % "|".join(REPEAT), re.IGNORECASE)


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


def email_user(profile, SUBJECT="", BODY=""):
    """
    sends an email.

    Arguments:
        profile -- contains information related to the user (e.g., email
                   address)
        SUBJECT -- subject line of the email
        BODY -- body text of the email
    """
    if not BODY:
        return False

    body = 'Hello %s,' % profile['first_name']
    body += '\n\n' + BODY.strip() + '\n\n'
    body += 'Best Regards,\nJasper\n'

    recipient = None

    if profile['prefers_email']:
        if profile['gmail_address']:
            recipient = profile['gmail_address']
            if profile['first_name'] and profile['last_name']:
                recipient = "%s %s <%s>" % (
                    profile['first_name'],
                    profile['last_name'],
                    recipient)
    else:
        if profile['carrier'] and profile['phone_number']:
            recipient = "%s@%s" % (
                str(profile['phone_number']),
                profile['carrier'])

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
        send_email(SUBJECT, body, recipient, user,
                   "Jasper <jasper>", password, server)

    except Exception:
        return False
    else:
        return True


def get_timezone(profile):
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
    return check_regex(NEGATIVE, phrase)


def is_positive(phrase):
    """
        Returns True if the input phrase has a positive sentiment.

        Arguments:
        phrase -- the input phrase to-be evaluated
    """
    return check_regex(POSITIVE, phrase)


def is_cancel(phrase):
    return check_regex(CANCEL, phrase)

def is_repeat(phrase):
    return check_regex(REPEAT, phrase)


def check_regex(pattern, phrase):
    if not phrase:
        return False
    if isinstance(phrase, list):
        phrase = " ".join(phrase)
    return bool(pattern.search(phrase))
