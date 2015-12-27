# -*- coding: utf-8 -*-
import Queue
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import logging


class Notifier(object):

    class NotificationClient(object):

        def __init__(self, queue, check_notification):
            self.queue = queue
            self.check_notification = check_notification
            self.timestamp = datetime.datetime.now()
            self.count = 0

        def run(self):
            self.timestamp = self.check_notification(self.queue, self.count)
            self.count += 1

    def __init__(self, profile, mic):
        self._logger = logging.getLogger(__name__)
        self.q = Queue.Queue()
        self.profile = profile
        self.mic = mic
        self.notifiers = []
        sched = BackgroundScheduler(timezone="UTC", daemon=True)
        sched.start()
        sched.add_job(self.gather,
                      'interval',
                      seconds=self.get_notification_interval())
        atexit.register(lambda: sched.shutdown(wait=False))

    def get_notification_interval(self):
        try:
            notification_interval = int(self.profile['notification_interval'])
        except KeyError:
            notification_interval = 30
            self._logger.warning("notification_interval not specified in " +
                                 "profile, using default of 30.")
        except ValueError:
            notification_interval = 30
            self._logger.warning("Invalid notification_interval specified. " +
                                 "Must be integer (seconds). Using 30.")
        return notification_interval

    def gather(self):
        for client in self.notifiers:
            if client.timestamp < datetime.datetime.now():
                client.run()
        notifications = self.get_all_notifications()
        for notif in notifications:
            self._logger.info("Received notification: '%s'", str(notif))
            self.mic.say(str(notif))

    def add_notification_client(self, check_notification):
        self.notifiers.append(self.NotificationClient(self.q,
                                                      check_notification))

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
