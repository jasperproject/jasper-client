# -*- coding: utf-8 -*-
import collections
import datetime
import dateutil
import requests
from jasper import plugin

YAHOO_YQL_QUERY_WOEID = \
    'SELECT * FROM geo.places WHERE text="%s"'
YAHOO_YQL_QUERY_FORECAST = \
    'SELECT * FROM weather.forecast WHERE woeid="%s" AND u="%s"'
YAHOO_YQL_URL = 'https://query.yahooapis.com/v1/public/yql'
YAHOO_YQL_WEATHER_CONDITION_CODES = {
    0:    'tornado',
    1:    'tropical storm',
    2:    'hurricane',
    3:    'severe thunderstorms',
    4:    'thunderstorms',
    5:    'mixed rain and snow',
    6:    'mixed rain and sleet',
    7:    'mixed snow and sleet',
    8:    'freezing drizzle',
    9:    'drizzle',
    10:   'freezing rain',
    11:   'showers',
    12:   'showers',
    13:   'snow flurries',
    14:   'light snow showers',
    15:   'blowing snow',
    16:   'snow',
    17:   'hail',
    18:   'sleet',
    19:   'dust',
    20:   'foggy',
    21:   'haze',
    22:   'smoky',
    23:   'blustery',
    24:   'windy',
    25:   'cold',
    26:   'cloudy',
    27:   'mostly cloudy at night',
    28:   'mostly cloudy at day',
    29:   'partly cloudy at night',
    30:   'partly cloudy at day',
    31:   'clear at night',
    32:   'sunny',
    33:   'fair at night',
    34:   'fair at day',
    35:   'mixed rain and hail',
    36:   'hot',
    37:   'isolated thunderstorms',
    38:   'scattered thunderstorms',
    39:   'scattered thunderstorms',
    40:   'scattered showers',
    41:   'heavy snow',
    42:   'scattered snow showers',
    43:   'heavy snow',
    44:   'partly cloudy',
    45:   'thundershowers',
    46:   'snow showers',
    47:   'isolated thundershowers'
}

WEEKDAY_NAMES = {
    0: 'Sunday',
    1: 'Monday',
    2: 'Tuesday',
    3: 'Wednesday',
    4: 'Thursday',
    5: 'Friday',
    6: 'Saturday'
}

Weather = collections.namedtuple(
    'Weather', ['city', 'date', 'text', 'temp', 'forecast'])

ForecastItem = collections.namedtuple(
    'ForecastItem', ['text', 'date', 'temp_high', 'temp_low'])


def yql_json_request(yql_query):
    r = requests.get(YAHOO_YQL_URL,
                     params={
                        'q': yql_query,
                        'format': 'json',
                        'env': 'store://datatables.org/alltableswithkeys'},
                     headers={'User-Agent': 'Mozilla/5.0'})
    return r.json()


def get_woeid(location_name):
    yql_query = YAHOO_YQL_QUERY_WOEID % location_name.replace('"', '')
    r = requests.get(YAHOO_YQL_URL,
                     params={
                        'q': yql_query,
                        'format': 'json',
                        'env': 'store://datatables.org/alltableswithkeys'},
                     headers={'User-Agent': 'Mozilla/5.0'})
    content = r.json()
    try:
        place = content['query']['results']['place']
    except KeyError:
        return None

    # We just return the first match
    try:
        return int(place[0]['woeid'])
    except Exception:
        return None


def get_weather(woeid, unit="f"):
    yql_query = YAHOO_YQL_QUERY_FORECAST % (int(woeid),
                                            unit.replace('"', ''))
    content = yql_json_request(yql_query)
    # make sure we got data
    try:
        channel = content['query']['results']['channel']
    except KeyError:
        # return empty Weather
        return None
    current_date = dateutil.parser.parse(
        channel['item']['condition']['date']).date()
    forecast = []

    for item in channel['item']['forecast']:
        fc_date = datetime.datetime.strptime(item['date'], "%d %b %Y").date()
        if (fc_date - current_date).days > 0:
            forecast.append(ForecastItem(
                text=YAHOO_YQL_WEATHER_CONDITION_CODES[int(item['code'])],
                date=fc_date,
                temp_high=int(item['high']),
                temp_low=int(item['low'])))
    return Weather(city=channel['location']['city'],
                   date=current_date,
                   text=YAHOO_YQL_WEATHER_CONDITION_CODES[
                      int(channel['item']['condition']['code'])],
                   temp=int(channel['item']['condition']['temp']),
                   forecast=forecast)


class WeatherPlugin(plugin.SpeechHandlerPlugin):
    def __init__(self, *args, **kwargs):
        super(WeatherPlugin, self).__init__(*args, **kwargs)
        try:
            self._woeid = self.profile['weather']['woeid']
        except KeyError:
            try:
                location = self.profile['weather']['location']
            except KeyError:
                raise ValueError('Weather location not configured!')
            self._woeid = get_woeid(location)

        if not self._woeid:
            raise ValueError('Weather location (woeid) invalid!')

        try:
            unit = self.profile['weather']['unit']
        except KeyError:
            self._unit = 'f'
        else:
            unit = unit.lower()
            if unit == 'c' or unit == 'celsius':
                self._unit = 'c'
            elif unit == 'f' or unit == 'fahrenheit':
                self._unit = 'f'
            else:
                raise ValueError('Invalid unit!')

    def get_phrases(self):
        return [
            self.gettext("WEATHER"),
            self.gettext("TODAY"),
            self.gettext("TOMORROW"),
            self.gettext("TEMPERATURE"),
            self.gettext("FORECAST"),
            self.gettext("YES"),
            self.gettext("NO")]

    def handle(self, text, mic):
        """
        Responds to user-input, typically speech text, with a summary of
        the relevant weather for the requested date (typically, weather
        information will not be available for days beyond tomorrow).

        Arguments:
            text -- user-input, typically transcribed speech
            mic -- used to interact with the user (for both input and output)
        """

        weather = get_weather(self._woeid, unit=self._unit)

        if self.gettext('TOMORROW').upper() in text.upper():
            # Tomorrow
            self._say_forecast_tomorrow(mic, weather)
            return
        elif self.gettext('FORECAST').upper() in text.upper():
            # Forecast
            if len(weather.forecast) == 1:
                self._say_forecast_tomorrow(mic, weather)
            else:
                self._say_forecast(mic, weather)
        else:
            # Today
            msg = self.gettext(
                'Currently {text} at {temp} degrees in {city}.').format(
                    text=self.gettext(weather.text),
                    temp=weather.temp,
                    city=weather.city)
            if len(weather.forecast) == 0:
                mic.say(msg)
                return

            msg += ' '
            if len(weather.forecast) == 1:
                msg += self.gettext(
                    'Do you want to hear the forecast for tomorrow?')
            else:
                msg += (self.gettext('Do you want to hear the forecast ' +
                                     'for the next %d days?') %
                        len(weather.forecast))
            mic.say(msg)
            if any(self.gettext('YES').upper() in s.upper()
                   for s in mic.active_listen()):
                if len(weather.forecast) == 1:
                    self._say_forecast_tomorrow(mic, weather)
                else:
                    self._say_forecast(mic, weather)
            return

    def _say_forecast_tomorrow(self, mic, weather):
        tomorrow = None

        if weather is None:
            mic.say(self.gettext(
                "Sorry, I had a problem retrieving the weather data."))
            return

        for fc in weather.forecast:
            if fc.date - weather.date == datetime.timedelta(days=1):
                tomorrow = fc
        if tomorrow is not None:
            mic.say(self.gettext(
                'Tomorrow in {city}: {text} and temperatures ' +
                'between {temp_low} and {temp_high} degrees.').format(
                 city=weather.city,
                 text=self.gettext(fc.text),
                 temp_low=fc.temp_low,
                 temp_high=fc.temp_high))
        else:
            mic.say(self.gettext(
                "Sorry, I don't know what the weather in %s will " +
                "be like tomorrow.") % weather.city)

    def _say_forecast(self, mic, weather):
        forecast_msgs = []

        # no forecast available
        if weather is None:
            mic.say(self.gettext(
                "Sorry, I had a problem retrieving the weather data."))
            return

        for fc in weather.forecast:
            if fc.date - weather.date == datetime.timedelta(days=1):
                date = self.gettext('Tomorrow')
            else:
                date = self.gettext(WEEKDAY_NAMES[int(fc.date.strftime('%w'))])
            forecast_msgs.append("%s: %s" % (date, self.gettext(
                '{text} and temperatures between {temp_low} and ' +
                '{temp_high} degrees.').format(
                    text=self.gettext(fc.text),
                    temp_low=fc.temp_low,
                    temp_high=fc.temp_high)))
        mic.say((self.gettext('Weather Forecast for the next %d days: ')
                 % len(weather.forecast)) + '... '.join(forecast_msgs))

    def is_valid(self, text):
        """
            Returns True if the text is related to the weather.

            Arguments:
            text -- user-input, typically transcribed speech
        """
        text = text.upper()
        return (self.gettext('WEATHER').upper() in text or
                self.gettext('TEMPERATURE').upper() in text or
                self.gettext('FORECAST').upper() in text)
