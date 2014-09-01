#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import sys
import argparse
import socket
import traceback
import shutil

import yaml
import client.speaker 
from client.conversation import Conversation
import client.jasperpath as jasperpath
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
        self.config = yaml.safe_load(open(jasperpath.config("profile.yml"), "r"));

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
            print "stt_engine not specified in profile, defaulting to PocketSphinx"
            stt_engine_type = "sphinx"

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
        except:
            return False
        else:
            return True

    def create_config_dirs(self):
        for directory in [jasperpath.CONFIG_PATH, jasperpath.config("sentences"), jasperpath.config("languagemodels"), jasperpath.config("dictionaries")]:
            if not os.path.exists(directory):
                try:
                    os.mkdir(directory)
                except OSError(errno, strerror):
                    raise
                else:
                    pass

    def start_conversation(self):
        addendum = ""
        if 'first_name' in self.config:
            addendum = ", %s" % self.config["first_name"]
        self.audio.say("How can I be of service%s?" % addendum)
        conversation = Conversation("JASPER", self.audio, self.config)
        conversation.handleForever()

if __name__ == "__main__":
    print "==========================================================="
    print " JASPER The Talking Computer                               "
    print " Copyright 2013 Shubhro Saha & Charlie Marsh               "
    print "==========================================================="

    app = Jasper(compile=args.compile)

    if args.checknetwork:
        if app.has_network_connection():
            print "CONNECTED TO INTERNET"
        else:
            print "COULD NOT CONNECT TO NETWORK"
            traceback.print_exc()
            app.audio.say("Hello, I could not connect to a network. Please read the documentation to configure your network.")
            sys.exit(1)

    app.start_conversation()
