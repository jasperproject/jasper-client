#!/usr/bin/env python

import os
import urllib2
import sys

import vocabcompiler
import traceback

lib_path = os.path.abspath('../client')
sys.path.append(lib_path)

import speaker as speak
speaker = speak.newSpeaker()


def fail(message):
    traceback.print_exc()
    speaker.say(message)


def configure():
    try:
        urllib2.urlopen("http://www.google.com").getcode()

        print "CONNECTED TO INTERNET"
        print "COMPILING DICTIONARY"
        vocabcompiler.compile(
            "../client/sentences.txt", "../client/dictionary.dic", "../client/languagemodel.lm")

        print "STARTING CLIENT PROGRAM"
        os.system("$JASPER_HOME/jasper/client/start.sh &")

    except urllib2.URLError:
        print "COULD NOT CONNECT TO NETWORK"
        fail(
            "I could not connect to a network. Please read the documentation to configure your Raspberry Pi.")

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

if __name__ == "__main__":
    print "==========STARTING JASPER CLIENT=========="
    print "=========================================="
    print "COPYRIGHT 2013 SHUBHRO SAHA, CHARLIE MARSH"
    print "=========================================="
    speaker.say("Hello.... I am Jasper... Please wait one moment.")
    configure()
