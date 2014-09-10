#!/usr/bin/env python2

import os
import sys

# Set $JASPER_HOME
jasper_home = os.getenv("JASPER_HOME")
if not jasper_home or not os.path.exists(jasper_home):
    if os.path.exists("/home/pi"):
        jasper_home = "/home/pi"
        os.environ["JASPER_HOME"] = jasper_home
    else:
        print("Error: $JASPER_HOME is not set.")
        sys.exit(0)

# Change CWD to $JASPER_HOME/jasper/client
os.chdir(os.path.join(os.getenv("JASPER_HOME"), "jasper" , "client"))

# Set $LD_LIBRARY_PATH
os.environ["LD_LIBRARY_PATH"] = "/usr/local/lib"

# Set $PATH
path = os.getenv("PATH")
if path:
    path = os.pathsep.join([path, "/usr/local/lib/"])
else:
    path = "/usr/local/lib/"
os.environ["PATH"] = path

import urllib2
import traceback

import vocabcompiler
import speaker as speak
speaker = speak.newSpeaker()

def testConnection():
    try:
        urllib2.urlopen("http://www.google.com").getcode()
        print "CONNECTED TO INTERNET"

    except urllib2.URLError:
        print "COULD NOT CONNECT TO NETWORK"
        speaker.say(
            "Warning: I was unable to connect to a network. Parts of the system may not work correctly, depending on your setup.")

def fail(message):
    traceback.print_exc()
    speaker.say(message)
    #sys.exit(1)

def configure():
    try:
        print "COMPILING DICTIONARY"
        vocabcompiler.compile(
            "sentences.txt", "dictionary.dic", "languagemodel.lm")
        print "STARTING CLIENT PROGRAM"

    except OSError:
        print "BOOT FAILURE: OSERROR"
        fail(
            "There was a problem starting Jasper. You may be missing the language model and associated files. Please read the documentation to configure your Raspberry Pi.")

    except IOError:
        print "BOOT FAILURE: IOERROR"
        fail(
            "There was a problem starting Jasper. You may have set permissions incorrectly on some part of the filesystem. Please read the documentation to configure your Raspberry Pi.")

    except:
        print "BOOT FAILURE"
        fail(
            "There was a problem starting Jasper. Please read the documentation to configure your Raspberry Pi.")

import shutil

old_client = os.path.abspath(os.path.join(os.pardir, "old_client"))
if os.path.exists(old_client):
    shutil.rmtree(old_client)

import yaml
import stt
from conversation import Conversation

def isLocal():
    return len(sys.argv) > 1 and sys.argv[1] == "--local"

if isLocal():
    from local_mic import Mic
else:
    from mic import Mic

if __name__ == "__main__":

    print "==========================================================="
    print " JASPER The Talking Computer                               "
    print " Copyright 2013 Shubhro Saha & Charlie Marsh               "
    print "==========================================================="

    speaker.say("Hello.... I am Jasper... Please wait one moment.")
    testConnection()
    configure()

    profile = yaml.safe_load(open("profile.yml", "r"))

    try:
        api_key = profile['keys']['GOOGLE_SPEECH']
    except KeyError:
        api_key = None

    try:
        stt_engine_type = profile['stt_engine']
    except KeyError:
        print "stt_engine not specified in profile, defaulting to PocketSphinx"
        stt_engine_type = "sphinx"

    mic = Mic(speaker, stt.PocketSphinxSTT(),
              stt.newSTTEngine(stt_engine_type, api_key=api_key))

    addendum = ""
    if 'first_name' in profile:
        addendum = ", %s" % profile["first_name"]
    mic.say("How can I be of service%s?" % addendum)

    conversation = Conversation("JASPER", mic, profile)

    conversation.handleForever()
