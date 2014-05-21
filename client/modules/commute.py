import requests
import re

WORDS = ['COMMUTE', 'TIME TO WORK']

def handle(text, sender, receiver, profile):
    response = requests.get('http://commute.fitzgeralds.me/current?route_name=Lynnwood%20to%20Downtown%20Seattle')
    if response.status_code != 200:
        sender.say("Sorry, could not get traffic information at this time.")
    else:
        sender.say("Current travel time to Seattle is %d minutes" % (response.json().get('duration', 16) + 10))

def isValid(text):
    return bool(re.search(r'\b(traffic|commute|travel)\b', text, re.IGNORECASE))