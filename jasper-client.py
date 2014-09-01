#!/usr/bin/env python2
# -*- coding: utf-8-*-
import logging
import logging.config
import os.path
import client.jasperpath as jasperpath
def logging_init():
    logfile = jasperpath.data("logging.cfg")
    try:
        logging.config.fileConfig(logfile)
    except Exception:
        logging.basicConfig()
logging_init()
logger = logging.getLogger()

import sys
import argparse
import socket
import traceback
import shutil

import yaml
import client.speaker 
from client.conversation import Conversation
import client.stt
import client.g2p

parser = argparse.ArgumentParser()
parser.add_argument("--local", help="Use local_mic", action="store_true")
parser.add_argument("--checknetwork", help="Check if network connection is available", action="store_true")
parser.add_argument("--compile", help="Compile vocabulary on startup", action="store_true")
args = parser.parse_args()

if args.local:
    from client.local_mic import Mic
else:
    from client.mic import Mic

class Jasper(object):
    def __init__(self, compile=False):
        self.create_config_dirs()

        # Load config
        config_filename = jasperpath.config("profile.yml")
        logger.debug("Using config file: '%s'", config_filename)
        with open(config_filename, "r") as f:
            self.config = yaml.safe_load(f);

        try:
            client.stt.HMM_PATH = self.config['advanced_settings']['hmm']
        except KeyError:
            pass

        try:
            client.g2p.PHONETISAURUS_MODEL = self.config['advanced_settings']['fst']
        except KeyError:
            pass

        try:
            api_key = self.config['keys']['GOOGLE_SPEECH']
        except KeyError:
            api_key = None

        try:
            stt_engine_type = self.config['stt_engine']
        except KeyError:
            stt_engine_type = "sphinx"
            logger.info("stt_engine not specified in profile, defaulting to '%s'", stt_engine_type)
        else:
            logger.debug("Using stt_engine '%s' from profile", stt_engine_type)

        # create Audio IO
        speaker = client.speaker.newSpeaker()
        passive_stt_engine = client.stt.PocketSphinxSTT(compile=compile)
        active_stt_engine = client.stt.newSTTEngine(stt_engine_type, api_key=api_key)
        self.audio = Mic(speaker, passive_stt_engine, active_stt_engine)

    @property
    def has_network_connection(self):
        try:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            host = socket.gethostbyname("www.google.com")
            # connect to the host -- tells us if the host is actually
            # reachable
            s = socket.create_connection((host, 80), 2)
        except Exception:
            logger.debug('Network connection check failed.', exc_info=True)
            return False
        else:
            logger.debug('Network connection check successful.')
            return True

    def create_config_dirs(self):
        for directory in [jasperpath.CONFIG_PATH, jasperpath.config("sentences"), jasperpath.config("languagemodels"), jasperpath.config("dictionaries")]:
            if not os.path.exists(directory):
                try:
                    os.mkdir(directory)
                except OSError(errno, strerror):
                    logger.exception("Error creating config dir '%s'!", directory)
                    raise
                else:
                    logger.debug("Created config dir '%s'.", directory)

    def start_conversation(self):
        addendum = ""
        if 'first_name' in self.config:
            addendum = ", %s" % self.config["first_name"]
        self.audio.say("How can I be of service%s?" % addendum)
        conversation = Conversation("JASPER", self.audio, self.config)
        logger.debug('Starting to handle conversation...')
        conversation.handleForever()

if __name__ == "__main__":
    print "==========================================================="
    print " JASPER The Talking Computer                               "
    print " Copyright 2013 Shubhro Saha & Charlie Marsh               "
    print "==========================================================="

    app = Jasper(compile=args.compile)

    if args.checknetwork and not app.has_network_connection():
        logger.error('Network connection check failed, quitting...')
        app.audio.say("Hello, I could not connect to a network. Please read the documentation to configure your network.")
        sys.exit(1)

    app.start_conversation()
