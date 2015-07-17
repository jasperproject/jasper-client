# -*- coding: utf-8-*-
from mewe import dic
import re

WORDS = ["FIND", "MEANING", "OF"]


def getresults(text, mic):
    query = ' '.join(s for s in text.split() if s.upper() not in WORDS)
    results = dic.get(query)
    print('Fetched results are.')
    for i in results:
        print(i)


def handle(text, mic, profile):
    """
        Responds to user-input, by telling word meanings".
        Arguments:
        text -- user-input, ex - "Find meaning of 'elephant'"
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

    return bool(re.search('Meaning', text, re.IGNORECASE))
