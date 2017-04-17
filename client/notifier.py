# -*- coding: utf-8-*-
import Queue
import atexit
from modules import Gmail
from apscheduler.schedulers.background import BackgroundScheduler
import logging


class Notifier(object):

    class NotificationClient(object):

        def __init__(self, gather, timestamp):
            self.gather = gather
            self.timestamp = timestamp

        def run(self):
            self.timestamp = self.gather(self.timestamp)

    def __init__(self, profile):
        self._logger = logging.getLogger(__name__)
        self.q = Queue.Queue()
        self.profile = profile
        self.notifiers = []

        if 'gmail_address' in profile and 'gmail_password' in profile:
            self.notifiers.append(self.NotificationClient(
                self.handle_email_notifications, None))
        else:
            self._logger.warning('gmail_address or gmail_password not set ' +
                                 'in profile, Gmail notifier will not be used')

        sched = BackgroundScheduler(timezone="UTC", daemon=True)
        sched.start()
        sched.add_job(self.gather, 'interval', seconds=30)
        atexit.register(lambda: sched.shutdown(wait=False))

    def gather(self):
        [client.run() for client in self.notifiers]

    def handle_email_notifications(self, last_date):
        """Places new Gmail notifications in the Notifier's queue."""
        emails = Gmail.fetch_unread_emails(self.profile, since=last_date)
        if emails:
            last_date = Gmail.get_most_recent_date(emails)

        def style_email(e):
            return "New email from %s." % Gmail.get_sender(e)

        for e in emails:
            self.q.put(style_email(e))

        return last_date

    def get_notification(self):
        """Returns a notification. Note that this function is consuming."""
        try:
            notif = self.q.get(block=False)
            return notif
        except Queue.Empty:
            return None

    def get_all_notifications(self):
        """
            Return a list of notifications in chronological order.
            Note that this function is consuming, so consecutive calls
            will yield different results.
        """
        notifs = []

        notif = self.get_notification()
        while notif:
            notifs.append(notif)
            notif = self.get_notification()

        return notifs
