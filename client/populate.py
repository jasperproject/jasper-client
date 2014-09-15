# -*- coding: utf-8-*-
# python modules
import sys
import os
import re
import argparse
import tempfile
import shutil

if sys.version_info.major == 3:
    import urllib.parse as urlparse
    get_input = input
else:
    import urlparse
    get_input = raw_input

# third party modules
import pytz
import feedparser
import jasperpath
# jasper modules
import jasperconf

class EnterAgainException(Exception):
    pass

class ConfigPopulator(object):
    def __init__(self, config):
        self.config = config

    def prompt(self, variable, name, description=None, sanitize_func=None, checkdepends_func=None):
        if checkdepends_func is not None and not checkdepends_func(self):
            return
        if description:
            print(description)
        current_value = self.config.get(variable)
        if not self.sanitize_yesno(get_input("%s (Current Value is: %r). Edit? [yN] " % (name, current_value))):
            print("")
            return
        while True:
            try:
                value = get_input("Enter new value for '%s': " % name)
            except KeyboardInterrupt:
                print("")
                return
            else:
                if value and sanitize_func:
                    try:
                        value = sanitize_func(self, value)
                    except EnterAgainException as e:
                        print(str(e))
                        return
                break
        self.config.set(variable, value=value)
        print("'%s' set to %r\n" % ("/".join(variable), value))

    def run(self):
        print("Welcome to the Jasper profile populator")
        print("If you chose to edit a value, but then " + \
              "changed your mind and prefer not to " + \
              "enter the requested information, just " + \
              "hit CTRL + C.\n")

        for setting in self.SETTINGS:
            self.prompt(*setting)

    # sanitize funcs
    def sanitize_yesno(self, response):
        return response and response.lower() in ('y','yes','true','ok'):

    def sanitize_phonenumber(self, phonenumber):
        return re.sub(r'[^0-9]', '', phonenumber)

    def sanitize_carrier(self, carrier):
        if carrier == 'AT&T':
            return 'txt.att.net'
        elif carrier == 'Verizon':
            return 'vtext.com'
        elif carrier == 'T-Mobile':
            return 'tmomail.net'
        else:
            return carrier

    def sanitize_location(self, location):
        baseurl = 'http://rss.wunderground.com/auto/rss_full/'
        url = urlparse.urljoin(baseurl, location)
        feed = feedparser.parse(url)
        num_entries = len(feed['entries'])
        if num_entries == 0:
            raise EnterAgainException('Weather not found. Please try another location.')
        else:
            location_name = feed['feed']['description'][33:]
            print("Location is '%s'.", location_name)
            return location

    def sanitize_timezone(self, tz):
        try:
            pytz.timezone(tz)
        except pytz.UnknownTimezoneError:
            raise EnterAgainException("Not a valid timezone. Try again.")
        else:
            return tz

    def sanitize_sttengines(self, engine_id):
        try:
            idx = int(engine_id)
        except ValueError:
            try:
                idx = [name for name, desc in self.AVAILABLE_STT_ENGINES].index(engine_id)
            except IndexError:
                EnterAgainException("%r is neither a number nor a valid name. Can't recognize STT engine.", engine_id)
        else:
            idx -= 1
        try:
            name, desc = self.AVAILABLE_STT_ENGINES[idx]
        except IndexError:
            EnterAgainException("%r is neither a number nor a valid name. Can't recognize STT engine.", engine_id)
        else:
            return name

    # checkdepends funcs
    def checkdepends_key(self, key):
        return False if not self.config.get(key) else True

    # TODO: the next constant should be fetched from the stt module
    AVAILABLE_STT_ENGINES = [
        ("sphinx", "Pocketsphinx"),
        ("google", "Google Translate STT")
    ]

    SETTINGS = [  
        [ 
          ['first_name'], # variable
          'First Name',   # name
          None,          # description
          None,          # sanitize_func
          None           # checkdepends_func
        ],
        [
          ['last_name'],
          'Last Name',
          None,
          None,
          None
         ],
        [
          ['gmail_address'],
          'Gmail Adress',
          'Jasper uses your Gmail to send notifications. Alternatively, ' + \
            'you can skip this step (or just fill in the email address if ' + \
            'if you want to receive email notifications) and setup a' + \
            'Mailgun account, as at http://jasperproject.github.io/' + \
            'documentation/software/#mailgun.',
          None,
          None
        ],
        [
          ['gmail_password'],
          'Gmail Password',
          None,
          None,
          lambda x: x.checkdepends_key('gmail_address')
        ],
        [
          ['phone_number'],
          'Phone number',
          'Your phone number (no country code). Any dashes or spaces ' + \
            'will be removed for you',
          sanitize_phonenumber,
          None
        ],
        [
          ['carrier'],
          'Phone carrier (for sending text notifications)',
          "If you have a US phone number, you can enter one of the " + \
            "following: 'AT&T', 'Verizon', 'T-Mobile' (without the " + \
            "quotes). If your carrier isn't listed or you have an " + \
            "international number, go to " + \
            "http://www.emailtextmessages.com and enter the email " + \
            "suffix for your carrier (e.g., for Virgin Mobile, enter " + \
            "'vmobl.com'; for T-Mobile Germany, enter 't-d1-sms.de').",
          sanitize_carrier,
          lambda x: x.checkdepends_key('phone_number')
        ],
        [
          ['location'],
          'Location (for weather requests)',
          'Location should be a 5-digit US zipcode (e.g., 08544). ' + \
            'If you are outside the US, insert the name of your ' + \
            'nearest big town/city.',
          sanitize_location,
          None
        ],
        [
          ['timezone'],
          'Timezone',
          'Please enter a timezone from the list located in the TZ* ' + \
            ' column at http://en.wikipedia.org/wiki/' + \
            'List_of_tz_database_time_zones, or none at all.',
          sanitize_timezone,
          None
        ],
        [
          ['prefers_email'],
          'Email notifications',
          'Would you prefer to have notifications sent by email? ' + \
            'If not, Jasper will try to use text message instead.',
          sanitize_yesno,
          lambda x: (x.checkdepends_key('phonenumber') and x.checkdepends_key('gmail_address'))
        ],
        [
          ['stt_engine'],
          'Speech-To-Text (STT) engine',
          '\n'.join(['If you would like to choose a specific STT ' + \
            ' engine, please specify which.'] + ["  %d. %s" % (i, info[1]) \
            for i, info in enumerate(AVAILABLE_STT_ENGINES, start=1)]),
          sanitize_sttengines,
          lambda x: (len(x.AVAILABLE_STT_ENGINES) > 1)
        ],
        [
          ['keys','GOOGLE_SPEECH'],
          'Google API key',
          'To use the Google Translate TTS engine, you need an API key from ' + \
            'https://console.developers.google.com/.',
          None,
          lambda x: (x.config.get('stt_engine') == "google")
        ]
    ]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="profile file to edit", nargs="?", default=jasperconf.DEFAULT_CONFIG_TYPE.STANDARD_CONFIG_FILE)
    parser.add_argument("--new", help="Start a new file from default file (default if file does not exist)", action="store_true")
    args = parser.parse_args()
    
    if args.new or not os.path.exists(args.file):
        with tempfile.NamedTemporaryFile(suffix='.%s' % jasperconf.DEFAULT_CONFIG_TYPE.FILE_EXT, delete=False) as f:
            tmp_config_file = f.name    
        conf = jasperconf.DEFAULT_CONFIG_TYPE(fname=tmp_config_file)
        print("Starting a fresh config file...")
    else:
        conf = jasperconf.DEFAULT_CONFIG_TYPE(fname=args.file)

    print("Config file will be written to '%s'\n" % args.file)

    populator = ConfigPopulator(conf)
    populator.run()
    conf.save()

    if args.new:
        shutil.copy(tmp_config_file, args.file)
        os.remove(tmp_config_file)
