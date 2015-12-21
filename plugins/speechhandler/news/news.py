# -*- coding: utf-8 -*-
import collections
import urllib
import urlparse
import feedparser
from client import plugin
from client import app_utils

FEED_URL = 'https://news.google.de/news/feeds'

Article = collections.namedtuple('Article', ['title', 'link'])


def get_top_articles(language='en', num_headlines=5):
    feed = feedparser.parse("{url}?{query}".format(
        url=FEED_URL,
        query=urllib.urlencode({
            'ned': language,
            'output': 'rss',
        })))

    articles = []
    for entry in feed.entries:
        # Remove News source
        title = entry.title.rsplit(' - ', 1)[0].strip()
        # Skip headlines that aren't complete
        if title.endswith('...'):
            continue
        # Remove '+++'
        title = ''.join([s.strip() for s in title.split('+++')])

        try:
            link = urlparse.parse_qs(
                urlparse.urlsplit(entry.link).query)['url'][0]
        except Exception:
            link = entry['link']
        articles.append(Article(title=title, link=link))
        if len(articles) >= num_headlines:
            break
    return articles


class NewsPlugin(plugin.SpeechHandlerPlugin):
    def get_priority(self):
        return 3

    def get_phrases(self):
        return [
            self.gettext("NEWS"),
            self.gettext("HEADLINES"),
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
        mic.say(self.gettext("Pulling up the news..."))

        try:
            lang = self.profile['language'].split('-')[0]
        except KeyError:
            lang = 'en'

        articles = get_top_articles(language=lang, num_headlines=5)
        if len(articles) == 0:
            mic.say(self.gettext(
                "Sorry, I'm unable to get the latest headlines right now."))
            return

        text = self.gettext('These are the current top headlines...')
        text += ' '
        text += '... '.join(
            '%d) %s' % (i, a.title)
            for i, a in enumerate(articles, start=1))
        mic.say(text)

        if 'gmail_address' not in self.profile:
            return

        mic.say(self.gettext('Would you like me to send you these articles?'))

        answers = mic.active_listen()
        if any(self.gettext('YES').upper() in answer.upper()
               for answer in answers):
            mic.say(self.gettext("Sure, just give me a moment."))
            email_text = self.make_email_text(articles)
            email_sent = app_utils.email_user(
                self.profile,
                SUBJECT=self.gettext("Your Top Headlines"),
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
        text = self.gettext('These are the articles you requested:')
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
        return any((word.upper() in text.upper()) for word in
                   (self.gettext("NEWS"), self.gettext("HEADLINES")))
