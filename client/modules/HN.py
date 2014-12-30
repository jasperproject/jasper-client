# -*- coding: utf-8-*-
import urllib2
import re
import random
from bs4 import BeautifulSoup
from client import app_utils
from semantic.numbers import NumberService

WORDS = ["HACKER", "NEWS", "YES", "NO", "FIRST", "SECOND", "THIRD"]

PRIORITY = 4

URL = 'http://news.ycombinator.com'


class HNStory:

    def __init__(self, title, URL):
        self.title = title
        self.URL = URL


def getTopStories(maxResults=None):
    """
        Returns the top headlines from Hacker News.

        Arguments:
        maxResults -- if provided, returns a random sample of size maxResults
    """
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib2.Request(URL, headers=hdr)
    page = urllib2.urlopen(req).read()
    soup = BeautifulSoup(page)
    matches = soup.findAll('td', class_="title")
    matches = [m.a for m in matches if m.a and m.text != u'More']
    matches = [HNStory(m.text, m['href']) for m in matches]

    if maxResults:
        num_stories = min(maxResults, len(matches))
        return random.sample(matches, num_stories)

    return matches


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a sample of
        Hacker News's top headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    mic.say("Pulling up some stories.")
    stories = getTopStories(maxResults=3)
    all_titles = '... '.join(str(idx + 1) + ") " +
                             story.title for idx, story in enumerate(stories))

    def handleResponse(text):

        def extractOrdinals(text):
            output = []
            service = NumberService()
            for w in text.split():
                if w in service.__ordinals__:
                    output.append(service.__ordinals__[w])
            return [service.parse(w) for w in output]

        chosen_articles = extractOrdinals(text)
        send_all = not chosen_articles and app_utils.isPositive(text)

        if send_all or chosen_articles:
            mic.say("Sure, just give me a moment")

            if profile['prefers_email']:
                body = "<ul>"

            def formatArticle(article):
                tiny_url = app_utils.generateTinyURL(article.URL)

                if profile['prefers_email']:
                    return "<li><a href=\'%s\'>%s</a></li>" % (tiny_url,
                                                               article.title)
                else:
                    return article.title + " -- " + tiny_url

            for idx, article in enumerate(stories):
                if send_all or (idx + 1) in chosen_articles:
                    article_link = formatArticle(article)

                    if profile['prefers_email']:
                        body += article_link
                    else:
                        if not app_utils.emailUser(profile, SUBJECT="",
                                                   BODY=article_link):
                            mic.say("I'm having trouble sending you these " +
                                    "articles. Please make sure that your " +
                                    "phone number and carrier are correct " +
                                    "on the dashboard.")
                            return

            # if prefers email, we send once, at the end
            if profile['prefers_email']:
                body += "</ul>"
                if not app_utils.emailUser(profile,
                                           SUBJECT="From the Front Page of " +
                                                   "Hacker News",
                                           BODY=body):
                    mic.say("I'm having trouble sending you these articles. " +
                            "Please make sure that your phone number and " +
                            "carrier are correct on the dashboard.")
                    return

            mic.say("All done.")

        else:
            mic.say("OK I will not send any articles")

    if not profile['prefers_email'] and profile['phone_number']:
        mic.say("Here are some front-page articles. " +
                all_titles + ". Would you like me to send you these? " +
                "If so, which?")
        handleResponse(mic.activeListen())

    else:
        mic.say("Here are some front-page articles. " + all_titles)


def isValid(text):
    """
        Returns True if the input is related to Hacker News.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(hack(er)?|HN)\b', text, re.IGNORECASE))
