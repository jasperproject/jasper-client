# -*- coding: utf-8 -*-
import datetime
import facebook
from client.app_utils import get_timezone
from client import plugin


class BirthdayPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [self.gettext("BIRTHDAY")]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, by listing the user's
        Facebook friends with birthdays today.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        oauth_access_token = self.profile['keys']["FB_TOKEN"]

        graph = facebook.GraphAPI(oauth_access_token)

        try:
            results = graph.request("me/friends",
                                    args={'fields': 'id,name,birthday'})
        except facebook.GraphAPIError:
            mic.say(self.gettext(
                "I have not been authorized to query your Facebook. If you " +
                "would like to check birthdays in the future, please visit " +
                "the Jasper dashboard."))
            return
        except:
            mic.say(self.gettext("I apologize, there's a problem with that " +
                                 "service at the moment."))
            return

        needle = datetime.datetime.now(
            tz=get_timezone(self.profile)).strftime("%m/%d")

        people = []
        for person in results['data']:
            try:
                if needle in person['birthday']:
                    people.append(person['name'])
            except:
                continue

        if len(people) > 0:
            if len(people) == 1:
                output = self.gettext("%s has a birthday today.") % people[0]
            else:
                output = (self.gettext(
                    "Your friends with birthdays today are %s and %s.") %
                    (", ".join(people[:-1]), people[-1]))
        else:
            output = self.gettext("None of your friends have birthdays today.")

        mic.say(output)

    def is_valid(self, text):
        """
            Returns True if the input is related to birthdays.

            Arguments:
            text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
