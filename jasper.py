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

# Set $JASPER_HOME
if not os.getenv('JASPER_HOME'):
    os.environ["JASPER_HOME"]  = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

from client.diagnose import Diagnostics
from client import vocabcompiler, stt
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

# Change CWD to $JASPER_HOME/jasper/client
client_path = os.path.join(os.getenv("JASPER_HOME"), "jasper", "client")
os.chdir(client_path)
# Add $JASPER_HOME/jasper/client to sys.path
sys.path.append(client_path)

class Jasper(object):
    def __init__(self):
        # Read config
        config_file = os.path.abspath(os.path.join(client_path, 'profile.yml'))
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

        # Compile dictionary
        sentences, dictionary, languagemodel = [os.path.abspath(os.path.join(client_path, filename)) for filename in ("sentences.txt", "dictionary.dic", "languagemodel.lm")]
        vocabcompiler.compile(sentences, dictionary, languagemodel)

        # Initialize Mic
        self.mic = Mic(speak.newSpeaker(), stt.PocketSphinxSTT(), stt.newSTTEngine(stt_engine_type, api_key=api_key))

    def run(self):
        salutation = "How can I be of service, %s?" % self.config["first_name"] if 'first_name' in self.config else "How can I be of service?"
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
        logger.exception("Can't read config file.")
        sys.exit(1)
    except OSError:
        logger.exception("Language model or associated files missing.")
        sys.exit(1)
    except Exception():
        logger.exception("Unknown error occured")
        sys.exit(1)
    
    app.run()
