# -*- coding: utf-8-*-
import imaplib
import email
import re
from dateutil import parser

WORDS = ["EMAIL", "INBOX"]


def get_sender(email):
    """
        Returns the best-guess sender of an email.

        Arguments:
        email -- the email whose sender is desired

        Returns:
        Sender of the email.
    """
    sender = email['From']
    m = re.match(r'(.*)\s<.*>', sender)
    if m:
        return m.group(1)
    return sender


def get_date(email):
    return parser.parse(email.get('date'))


def get_most_recent_date(emails):
    """
        Returns the most recent date of any email in the list provided.

        Arguments:
        emails -- a list of emails to check

        Returns:
        Date of the most recent email.
    """
    dates = [get_date(e) for e in emails]
    dates.sort(reverse=True)
    if dates:
        return dates[0]
    return None


def fetch_unread_emails(profile, since=None, markRead=False, limit=None):
    """
        Fetches a list of unread email objects from a user's Gmail inbox.

        Arguments:
        profile -- contains information related to the user (e.g., Gmail
                   address)
        since -- if provided, no emails before this date will be returned
        markRead -- if True, marks all returned emails as read in target inbox

        Returns:
        A list of unread email objects.
    """
    conn = imaplib.IMAP4_SSL('imap.gmail.com')
    conn.debug = 0
    conn.login(profile['gmail_address'], profile['gmail_password'])
    conn.select(readonly=(not markRead))

    msgs = []
    (retcode, messages) = conn.search(None, '(UNSEEN)')

    if retcode == 'OK' and messages != ['']:
        numUnread = len(messages[0].split(' '))
        if limit and numUnread > limit:
            return numUnread

        for num in messages[0].split(' '):
            # parse email RFC822 format
            ret, data = conn.fetch(num, '(RFC822)')
            msg = email.message_from_string(data[0][1])

            if not since or get_date(msg) > since:
                msgs.append(msg)
    conn.close()
    conn.logout()

    return msgs


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the user's Gmail inbox, reporting on the number of unread emails
        in the inbox, as well as their senders.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., Gmail
                   address)
    """
    try:
        msgs = fetch_unread_emails(profile, limit=5)

        if isinstance(msgs, int):
            response = "You have %d unread emails." % msgs
            mic.say(response)
            return

        senders = [get_sender(e) for e in msgs]
    except imaplib.IMAP4.error:
        mic.say(
            "I'm sorry. I'm not authenticated to work with your Gmail.")
        return

    if not senders:
        mic.say("You have no unread emails.")
    elif len(senders) == 1:
        mic.say("You have one unread email from " + senders[0] + ".")
    else:
        response = "You have %d unread emails" % len(
            senders)
        unique_senders = list(set(senders))
        if len(unique_senders) > 1:
            unique_senders[-1] = 'and ' + unique_senders[-1]
            response += ". Senders include: "
            response += '...'.join(senders)
        else:
            response += " from " + unique_senders[0]

        mic.say(response)


def is_valid(text):
    """
        Returns True if the input is related to email.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bemail\b', text, re.IGNORECASE))
