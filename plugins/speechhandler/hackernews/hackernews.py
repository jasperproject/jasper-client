# -*- coding: utf-8 -*-
import collections
import requests
from jasper import app_utils
from jasper import plugin

HN_TOPSTORIES_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
HN_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/%d.json'

Article = collections.namedtuple('Article', ['title', 'link'])


def get_top_articles(num_headlines=5):
    r = requests.get(HN_TOPSTORIES_URL)
    item_ids = r.json()
    articles = []
    for i, item_id in enumerate(item_ids, start=1):
        r = requests.get(HN_ITEM_URL % item_id)
        item = r.json()
        articles.append(Article(title=item['title'], link=item['url']))
        if i >= num_headlines:
            break
    return articles


class HackerNewsPlugin(plugin.SpeechHandlerPlugin):
    def __init__(self, *args, **kwargs):
        super(HackerNewsPlugin, self).__init__(*args, **kwargs)

        self._num_headlines = int(self.config.get('hacker-news',
                                                  'num-headlines'))

    def get_priority(self):
        return 4

    def get_phrases(self):
        return [
            self.gettext("HACKER"),
            self.gettext("NEWS"),
            self.gettext("YES"),
            self.gettext("NO")]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, with a summary of
        the day's top news headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        mic.say(self.gettext("Getting the top %d stories from Hacker News...")
                % self._num_headlines)

        articles = get_top_articles(num_headlines=self._num_headlines)
        if len(articles) == 0:
            mic.say(self.gettext(
                "Sorry, I'm unable to get the top stories from " +
                "Hacker News right now."))
            return

        text = self.gettext('These are the current top stories...')
        text += ' '
        text += '... '.join(
            '%d) %s' % (i, a.title)
            for i, a in enumerate(articles, start=1))
        mic.say(text)

        if not self.config.get('gmail_address'):
            return

        mic.say(self.gettext('Would you like me to send you these articles?'))

        answers = mic.active_listen()
        if any(self.gettext('YES').upper() in answer.upper()
               for answer in answers):
            mic.say(self.gettext("Sure, just give me a moment."))
            email_text = self.make_email_text(articles)
            email_sent = app_utils.email_user(
                self.config,
                SUBJECT=self.gettext("Top Stories from Hacker News"),
                BODY=email_text)
            if email_sent:
                mic.say(self.gettext(
                    "Okay, I've sent you an email."))
            else:
                mic.say(self.gettext(
                    "Sorry, I'm having trouble sending you these articles."))
        else:
            mic.say(self.gettext("Okay, I will not send any articles."))

    def make_email_text(self, articles):
        text = self.gettext(
            'These are the Hacker News articles you requested:')
        text += '\n\n'
        for article in articles:
            text += '- %s\n  %s\n' % (article.title, article.link)
        return text

    def is_valid(self, text):
        """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return (self.gettext('HACKER').upper() in text.upper())
