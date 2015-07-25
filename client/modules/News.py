# -*- coding: utf-8-*-
import feedparser
from client import app_utils
import re
from semantic.numbers import NumberService

WORDS = ["NEWS", "YES", "NO", "FIRST", "SECOND", "THIRD"]

PRIORITY = 3

URL = 'http://news.ycombinator.com'


class Article:

    def __init__(self, title, URL):
        self.title = title
        self.URL = URL


def get_top_articles(max_results=None):
    d = feedparser.parse("http://news.google.com/?output=rss")

    count = 0
    articles = []
    for item in d['items']:
        articles.append(Article(item['title'], item['link'].split("&url=")[1]))
        count += 1
        if max_results and count > max_results:
            break

    return articles


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the day's top news headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    mic.say("Pulling up the news")
    articles = get_top_articles(max_results=3)
    titles = [" ".join(x.title.split(" - ")[:-1]) for x in articles]
    all_titles = "... ".join(str(idx + 1) + ")" +
                             title for idx, title in enumerate(titles))

    def handle_response(text):

        def extract_ordinals(text):
            output = []
            service = NumberService()
            for w in text.split():
                if w in service.__ordinals__:
                    output.append(service.__ordinals__[w])
            return [service.parse(w) for w in output]

        chosen_articles = extract_ordinals(text)
        send_all = not chosen_articles and app_utils.is_positive(text)

        if send_all or chosen_articles:
            mic.say("Sure, just give me a moment")

            if profile['prefers_email']:
                body = "<ul>"

            def format_article(article):
                tiny_url = app_utils.generate_tiny_URL(article.URL)

                if profile['prefers_email']:
                    return "<li><a href=\'%s\'>%s</a></li>" % (tiny_url,
                                                               article.title)
                else:
                    return article.title + " -- " + tiny_url

            for idx, article in enumerate(articles):
                if send_all or (idx + 1) in chosen_articles:
                    article_link = format_article(article)

                    if profile['prefers_email']:
                        body += article_link
                    else:
                        if not app_utils.email_user(profile, SUBJECT="",
                                                    BODY=article_link):
                            mic.say("I'm having trouble sending you these " +
                                    "articles. Please make sure that your " +
                                    "phone number and carrier are correct " +
                                    "on the dashboard.")
                            return

            # if prefers email, we send once, at the end
            if profile['prefers_email']:
                body += "</ul>"
                if not app_utils.email_user(profile,
                                            SUBJECT="Your Top Headlines",
                                            BODY=body):
                    mic.say("I'm having trouble sending you these articles. " +
                            "Please make sure that your phone number and " +
                            "carrier are correct on the dashboard.")
                    return

            mic.say("All set")

        else:

            mic.say("OK I will not send any articles")

    if 'phone_number' in profile:
        mic.say("Here are the current top headlines. " + all_titles +
                ". Would you like me to send you these articles? " +
                "If so, which?")
        handle_response(mic.activeListen())

    else:
        mic.say(
            "Here are the current top headlines. " + all_titles)


def is_valid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(news|headline)\b', text, re.IGNORECASE))
