#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import re
from getpass import getpass
import yaml
from pytz import timezone
import feedparser
import jasperpath


def run():
    profile = {}

    """
    Prompt the user for the value of a field to save in the profile
    Puts the response in the profile and Returns 'True' if one was provided
    Returns 'False' otherwise
    """
    def simple_request(var, prompt, clean_input=None):
        input = raw_input(prompt + ": ")
        if input:
            if clean_input:
                input = clean_input(input)
            profile[var] = input
            return True
        return False

    """
    Prompt the user for the value of a field to save in the profile
    Keeps prompting until the value of the input, when evaluated
    with condition, is True
    Puts the response in the profile and Returns 'True' if one was provided
    Returns 'False' otherwise
    """
    def request_with_condition(var, prompt, condition, clean_input=None):
        input = raw_input(prompt + ": ")
        while input and not condition(input):
            input = raw_input(prompt + ": ")
        if input:
            if clean_input:
                input = clean_input(input)
            profile[var] = input
            return True
        return False

    print("Welcome to the profile populator. If, at any step, you'd prefer " +
          "not to enter the requested information, just hit 'Enter' with a " +
          "blank field to continue.")

    # name
    print("\nHow do you want Jasper to address you?")
    simple_request('first_name', 'First name')
    simple_request('last_name', 'Last name')

    # persona
    print("\nJasper, by default, listens for 'JASPER' keyword to get in the " +
          "mode to start processing your requests.")
    print("If you change the default keyword, remember to update the " +
          "keyword_phrases, dictionary_persona.dic and " +
          "languagemodel_persona.lm files in the 'static' folder.")
    print("You can upload the updated keyword file to " +
          "http://www.speech.cs.cmu.edu/tools/lmtool-new.html to recompile " +
          "the dictionary and language model, then copy the generated files "
          "to the appropriate locations")
    simple_request('persona', 'Persona')

    # gmail
    print("\nJasper uses your Gmail to send notifications. Alternatively, " +
          "you can skip this step (or just fill in the email address if you " +
          "want to receive email notifications) and setup a Mailgun " +
          "account, as at http://jasperproject.github.io/documentation/" +
          "software/#mailgun.")
    if simple_request('gmail_address', 'Gmail address'):
        profile['gmail_password'] = getpass()

    # phone number
    def clean_number(s):
        return re.sub(r'[^0-9]', '', s)

    print("\nPhone number (no country code).")
    print("Any dashes or spaces will be removed for you")
    simple_request('phone_number', 'Number', clean_number)

    # carrier
    sample_carriers = {
        "AT&T": "txt.att.net",
        "Verizon": "vtext.com",
        "T-Mobile": "tmomail.net"
    }

    def substitute_carrier(carrier):
        if carrier in sample_carriers:
            return sample_carriers[carrier]
        return carrier

    print("\nPhone carrier (for sending text notifications).")
    print("If you have a US phone number, you can enter one of the " +
          "following: 'AT&T', 'Verizon', 'T-Mobile' (without the quotes). " +
          "If your carrier isn't listed or you have an international " +
          "number, go to http://www.emailtextmessages.com and enter the " +
          "email suffix for your carrier (e.g., for Virgin Mobile, enter " +
          "'vmobl.com'; for T-Mobile Germany, enter 't-d1-sms.de').")
    simple_request('carrier', 'Carrier', substitute_carrier)

    # location
    def verify_location(place):
        feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/' +
                                place)
        num_entries = len(feed['entries'])
        if num_entries == 0:
            print("Weather not found. Please try another location.")
            return False
        else:
            print("Location saved as " + feed['feed']['description'][33:])
            return True

    print("\nLocation should be a 5-digit US zipcode (e.g., 08544). If you " +
          "are outside the US, insert the name of your nearest big " +
          "town/city.  For weather requests.")
    request_with_condition('location', 'Location', verify_location)

    # timezone
    def verify_timezone(tz):
        try:
            timezone(tz)
            return True
        except:
            print("Not a valid timezone. Try again.")
            return False

    print("\nPlease enter a timezone from the list located in the TZ* " +
          "column at http://en.wikipedia.org/wiki/" +
          "List_of_tz_database_time_zones, or none at all.")
    request_with_condition('timezone', 'Timezone', verify_timezone)

    # notifications
    def verify_notification_method(method):
        return method == 'E' or method == 'T'

    def substitute_notification_method(method):
        return method == 'E'

    print("\nWould you prefer to have notifications sent by")
    request_with_condition('prefers_email', 'Please choose email (E) or " ' +
                           'text message (T)', verify_notification_method,
                           substitute_notification_method)

    # stt engine
    stt_engines = ["att", "google", "julius", "sphinx", "witai"]

    def verify_stt_engine(engine):
        if engine not in stt_engines:
            print("Unrecognized STT engine. Available implementations: %s"
                  % stt_engines)
            return False
        return True

    print("\nIf you would like to choose a specific STT engine, please " +
          "specify which.")
    print("Available implementations: %s." % stt_engines +
          "(Press Enter to default to PocketSphinx)")
    if request_with_condition('stt_engine', 'STT Engine', verify_stt_engine):
        chosen_stt = profile["stt_engine"]
        if chosen_stt == 'att':
            key = raw_input('APP key: ')
            secret = raw_input('APP secret: ')
            profile["att-stt"] = {
                "app_key": key,
                "app_secret": secret
            }
        elif chosen_stt == 'google':
            key = raw_input('API key: ')
            profile["keys"] = {"GOOGLE_SPEECH": key}
        elif chosen_stt == 'julius':
            hmmdefs = raw_input("Path to your hmmdefs: ")
            tiedlist = raw_input("Path to your tiedlist: ")
            lexicon = raw_input("Path to your lexicon: ")
            lexicon_archive_member = raw_input("Lexicon Archive Member: ")
            profile["julius"] = {
                "hmmdefs": hmmdefs,
                "tiedlist": tiedlist,
                "lexicon": lexicon,
                "lexicon_archive_member": lexicon_archive_member
            }
        elif chosen_stt == 'witai':
            token = raw_input('Access Token: ')
            profile["witai-stt"] = {"access_token": token}
    else:
        profile["stt_engine"] = "sphinx"

    # tts engine
    tts_engines = ["espeak-tts", "festival-tts", "flite-tts", "google-tts",
                   "ivona-tts", "mary-tts", "osx-tts", "pico-tts"]

    def verify_tts_engine(engine):
        if engine not in tts_engines:
            print("Unrecognized TTS engine. Available implementations: %s"
                  % tts_engines)
            return False
        return True

    print("\nIf you would like to choose a specific TTS engine, please " +
          "specify which.")
    print("Available implementations: %s." % tts_engines +
          "(Press Enter to default to espeak)")
    if request_with_condition('tts_engine', 'TTS Engine', verify_tts_engine):
        chosen_tts = profile["tts_engine"]
        if chosen_tts == 'ivona-tts':
            access = raw_input('Access Key: ')
            secret = raw_input('Secret Key: ')
            profile["ivona-tts"] = {
                "access_key": access,
                "secret_key": secret
            }
        elif chosen_tts == 'mary-tts':
            server = raw_input("Server: ")
            port = raw_input("Port: ")
            language = raw_input("Language: ")
            voice = raw_input("Voice: ")
            profile["mary-tts"] = {
                "server": server,
                "port": port,
                "language": language,
                "voice": voice
            }
    else:
        profile["tts_engine"] = "espeak-tts"

    # write to profile
    print("\nWriting to profile...")
    if not os.path.exists(jasperpath.CONFIG_PATH):
        os.makedirs(jasperpath.CONFIG_PATH)
    profile_path = jasperpath.config("profile.yml")
    if os.path.exists(profile_path):
        print("Found an old configuration file. Renaming it with suffix -old")
        os.rename(profile_path, profile_path+"-old")
    outputFile = open(profile_path, "w")
    yaml.dump(profile, outputFile, default_flow_style=False)
    print("Done.")

if __name__ == "__main__":
    run()
