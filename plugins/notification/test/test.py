# -*- coding: utf-8 -*-
from client import plugin
import datetime


class TestPlugin(plugin.NotificationPlugin):
    """
    This is a test notification plugin to demonstrate use cases.
    """
    def check_notification(self, queue, count):
        """
        The method that needs to be overriden by every NotificationPlugin.

        queue can be used to send messages to be spoken to the user.
        count is the number of times this function has been executed.

        Should return the next datetime Jasper will attempt to re-run the
        method.
        """
        # Notify the user of the number of times this notification has run
        # Don't enable this functionality for now
        # queue.put('%s times' % count)
        self.timestamp = datetime.datetime.now()
        # Ask Jasper to re-run this method every minute
        return self.timestamp + datetime.timedelta(seconds=60)
