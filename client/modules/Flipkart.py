# -*- coding: utf-8-*-
import requests
from bs4 import BeautifulSoup
import re

WORDS = ["SEARCH", "FOR", "ON", "FLIPKART"]


def getresults(text, mic):
    query = ' '.join(s for s in text.split() if s.upper() not in WORDS)
    query = query.replace(' ', '+')
    url = "http://www.flipkart.com/search?q=" + str(query)
    url = url + "&as=off&as-show=on&otracker=start"

    page = requests.get(url)
    src = page.text
    ob = BeautifulSoup(src)

    ctr = 0
    mic.say("Top 5 results are")

    for a, b in zip(ob.findAll('div', {'class': 'pu-final'}),
        ob.findAll('a', {'class': 'fk-display-block'})):
        price = a.text
        title = b.text
        ctr = ctr + 1
        mic.say(title.strip() + " " + price.strip().replace('Rs.', 'Rupees'))
        if ctr == 5:
            break


def handle(text, mic, profile):
    """
        Responds to user-input, by telling top products on flipkart".
        Arguments:
        text -- user-input, ex - "Search for half girlfriend on flipkart"
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user
    """
    getresults(text, mic)


def isValid(text):
    """
      Returns True if the input is related to flipkart.

      Arguments:
      text -- user-input, typically transcribed speech
    """

    return bool(re.search(r'\bFlipkart\b', text, re.IGNORECASE))
