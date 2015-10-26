# -*- coding: utf-8 -*-
import imaplib
import email
import re
from dateutil import parser
from client import plugin


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


class GmailPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("EMAIL"), self.gettext("INBOX")]

    def fetch_unread_emails(self, since=None, markRead=False, limit=None):
        """
            Fetches a list of unread email objects from a user's Gmail inbox.

            Arguments:
            since -- if provided, no emails before this date will be returned
            markRead -- if True, marks all returned emails as read in target
                        inbox

            Returns:
            A list of unread email objects.
        """
        conn = imaplib.IMAP4_SSL('imap.gmail.com')
        conn.debug = 0
        conn.login(self.profile['gmail_address'],
                   self.profile['gmail_password'])
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

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, with a summary of
        the user's Gmail inbox, reporting on the number of unread emails
        in the inbox, as well as their senders.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        try:
            messages = self.fetch_unread_emails(limit=5)
        except imaplib.IMAP4.error:
            mic.say(self.gettext(
                "I'm sorry. I'm not authenticated to work with your Gmail."))
            return

        if isinstance(messages, int):
            if messages == 0:
                response = self.gettext("You have no unread emails.")
            elif messages == 1:
                response = self.gettext("You have one unread email.")
            else:
                response = (self.gettext("You have %d unread emails.") %
                            messages)
            mic.say(response)
            return

        senders = [get_sender(e) for e in messages]

        if not senders:
            mic.say(self.gettext("You have no unread emails."))
        elif len(senders) == 1:
            mic.say(self.gettext("You have one unread email from %s.") %
                    senders[0])
        else:
            response = self.gettext("You have %d unread emails.") % len(
                senders)
            unique_senders = list(set(senders))
            if len(unique_senders) > 1:
                response += " " + (self.gettext("Senders include %s and %s") %
                                   ', '.join(unique_senders[:-1]),
                                   unique_senders[-1])
            else:
                response += " " + (self.gettext("They are all from %s.") %
                                   unique_senders[0])
            mic.say(response)

    def is_valid(self, text):
        """
        Returns True if the input is related to email.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
