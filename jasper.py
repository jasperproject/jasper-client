#!/usr/bin/env python2
import os
import sys
import traceback
import shutil
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

import yaml
import argparse

from client.diagnose import Diagnostics
from client import vocabcompiler, stt, jasperpath
from client import speaker as speak
from client.conversation import Conversation

parser = argparse.ArgumentParser(description='Jasper Voice Control Center')
parser.add_argument('--local', action='store_true', help='Use text input instead of a real microphone')
parser.add_argument('--no-network-check', action='store_true', help='Disable the network connection check')
parser.add_argument('--debug', action='store_true', help='Show debug messages')
args = parser.parse_args()

if args.debug:
    logger.setLevel(logging.DEBUG)

if args.local:
    from client.local_mic import Mic
else:
    from client.mic import Mic

# Change CWD to jasperpath.LIB_PATH
os.chdir(jasperpath.LIB_PATH)
# Add jasperpath.LIB_PATH to sys.path
sys.path.append(jasperpath.LIB_PATH)

class Jasper(object):
    def __init__(self):
        # Read config
        config_file = os.path.abspath(os.path.join(jasperpath.LIB_PATH, 'profile.yml'))
        logger.debug("Trying to read config file: '%s'", config_file)
        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

        try:
            api_key = self.config['keys']['GOOGLE_SPEECH']
        except KeyError:
            api_key = None

        try:
            stt_engine_type = self.config['stt_engine']
        except KeyError:
            stt_engine_type = "sphinx"
            logger.warning("stt_engine not specified in profile, defaulting to '%s'", stt_engine_type)

        try:
            tts_engine_slug = self.config['tts_engine']
        except KeyError:
            tts_engine_slug = speak.get_default_engine_slug()
            logger.warning("tts_engine not specified in profile, defaulting to '%s'", tts_engine_slug)
        tts_engine = speak.get_engine_by_slug(tts_engine_slug)

        # Compile dictionary
        sentences, dictionary, languagemodel = [os.path.abspath(os.path.join(jasperpath.LIB_PATH, filename)) for filename in ("sentences.txt", "dictionary.dic", "languagemodel.lm")]
        vocabcompiler.compile(sentences, dictionary, languagemodel)

        # Initialize Mic
        self.mic = Mic(tts_engine(), stt.PocketSphinxSTT(), stt.newSTTEngine(stt_engine_type, api_key=api_key))

    def run(self):
        if 'first_name' in self.config:
            salutation = "How can I be of service, %s?" % self.config["first_name"]
        else:
            salutation = "How can I be of service?"
        self.mic.say(salutation)

        conversation = Conversation("JASPER", self.mic, self.config)
        conversation.handleForever()

if __name__ == "__main__":

    print "==========================================================="
    print " JASPER The Talking Computer                               "
    print " Copyright 2013 Shubhro Saha & Charlie Marsh               "
    print "==========================================================="

    if not args.no_network_check and not Diagnostics.check_network_connection():
        logger.warning("Network not connected. This may prevent Jasper from running properly.")

    try:
        app = Jasper()
    except IOError:
        logger.exception("Can't read profile file.")
        sys.exit(1)
    except OSError:
        logger.exception("Language model or associated files missing.")
        sys.exit(1)
    except Exception():
        logger.exception("Unknown error occured")
        sys.exit(1)
    
    app.run()
