import re
import datetime
import feedparser
from app_utils import getTimezone
from semantic.dates import DateService

WORDS = ["WEATHER", "TODAY", "TOMORROW"]


def replaceAcronyms(text):
    """Replaces some commonly-used acronyms for an improved verbal weather report."""

    def parseDirections(text):
        words = {
            'N': 'north',
            'S': 'south',
            'E': 'east',
            'W': 'west',
        }
        output = [words[w] for w in list(text)]
        return ' '.join(output)
    acronyms = re.findall(r'\b([NESW]+)\b', text)

    for w in acronyms:
        text = text.replace(w, parseDirections(w))

    text = re.sub(r'(\b\d+)F(\b)', '\g<1> Fahrenheit\g<2>', text)
    text = re.sub(r'(\b)mph(\b)', '\g<1>miles per hour\g<2>', text)
    text = re.sub(r'(\b)in\.', '\g<1>inches', text)

    return text


def getForecast(profile):
    return feedparser.parse("http://rss.wunderground.com/auto/rss_full/"
                            + str(profile['location']))['entries']


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the relevant weather for the requested date (typically, weather
        information will not be available for days beyond tomorrow).

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """

    if not profile['location']:
        mic.say(
            "I'm sorry, I can't seem to access that information. Please make sure that you've set your location on the dashboard.")
        return

    tz = getTimezone(profile)

    service = DateService(tz=tz)
    date = service.extractDay(text)
    if not date:
        date = datetime.datetime.now(tz=tz)
    weekday = service.__daysOfWeek__[date.weekday()]

    if date.weekday() == datetime.datetime.now(tz=tz).weekday():
        date_keyword = "Today"
    elif date.weekday() == (
            datetime.datetime.now(tz=tz).weekday() + 1) % 7:
        date_keyword = "Tomorrow"
    else:
        date_keyword = "On " + weekday

    forecast = getForecast(profile)

    output = None

    for entry in forecast:
        try:
            date_desc = entry['title'].split()[0].strip().lower()
            if date_desc == 'forecast': #For global forecasts
            	date_desc = entry['title'].split()[2].strip().lower()
            	weather_desc = entry['summary']

            elif date_desc == 'current': #For first item of global forecasts
            	continue
            else:
            	weather_desc = entry['summary'].split('-')[1] #US forecasts

            if weekday == date_desc:
                output = date_keyword + \
                    ", the weather will be " + weather_desc + "."
                break
        except:
            continue

    if output:
        output = replaceAcronyms(output)
        mic.say(output)
    else:
        mic.say(
            "I'm sorry. I can't see that far ahead.")


def isValid(text):
    """
        Returns True if the text is related to the weather.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(weathers?|temperature|forecast|outside|hot|cold|jacket|coat|rain)\b', text, re.IGNORECASE))
