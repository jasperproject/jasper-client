#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import sys
import argparse
import socket
import traceback
import shutil

import yaml
import client.vocabcompiler
import client.speaker 
from client.conversation import Conversation
import client.jasperpath as jasperpath

parser = argparse.ArgumentParser()
parser.add_argument("--local", help="Use local_mic", action="store_true")
parser.add_argument("--checknetwork", help="Check if network connection is available", action="store_true")
parser.add_argument("--compile", help="Compile vocabulary on startup", action="store_true")
args = parser.parse_args()

if args.local:
    from client.local_mic import Mic
else:
    from client.mic import Mic

def has_network_connection():
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

if __name__ == "__main__":
    print "==========================================================="
    print " JASPER The Talking Computer                               "
    print " Copyright 2013 Shubhro Saha & Charlie Marsh               "
    print "==========================================================="

    tempspeaker = client.speaker.newSpeaker()
    #tempspeaker.say("Hello.... I am Jasper... Please wait one moment.")

    for directory in [jasperpath.CONFIG_PATH, jasperpath.config("languagemodels"), jasperpath.config("dictionaries")]:
        if not os.path.exists(directory):
            try:
                os.mkdir(directory)
            except OSError(errno, strerror):
                print("Can't create configdir '%s': %s" % (directory, strerror))
                tempspeaker.say("Hello, I could not access the configuration directory or one of its subdirectories. Please check if you have the right permissions.")
                sys.exit(1)


    if args.checknetwork:
        if has_network_connection():
            print "CONNECTED TO INTERNET"
        else:
            print "COULD NOT CONNECT TO NETWORK"
            traceback.print_exc()
            tempspeaker.say("Hello, I could not connect to a network. Please read the documentation to configure your network.")
            sys.exit(1)

    if args.compile:
        print "COMPILING DICTIONARY"
        client.vocabcompiler.compile("dictionary","languagemodel")

    profile = yaml.safe_load(open(jasperpath.config("profile.yml"), "r"));

    mic = Mic(client.speaker.newSpeaker(), \
        jasperpath.languagemodel("languagemodel"), \
        jasperpath.dictionary("dictionary"), \
        jasperpath.data("vocab", "languagemodel_persona.lm"), \
        jasperpath.data("vocab", "dictionary_persona.dic"))

    del tempspeaker

    addendum = ""
    if 'first_name' in profile:
        addendum = ", %s" % profile["first_name"]
    #mic.say("How can I be of service%s?" % addendum)

    conversation = Conversation("JASPER", mic, profile)

    try:
        conversation.handleForever()
    except:
        sys.exit(1)
