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

# Change CWD to $JASPER_HOME/jasper/boot
os.chdir(os.path.join(os.getenv("JASPER_HOME"), "jasper", "boot"))

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

lib_path = os.path.abspath('../client')
sys.path.append(lib_path)

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


def configure():
    try:
        print "COMPILING DICTIONARY"
        vocabcompiler.compile(
            "../client/sentences.txt", "../client/dictionary.dic", "../client/languagemodel.lm")
        print "STARTING CLIENT PROGRAM"
        os.system("$JASPER_HOME/jasper/client/start.sh &")

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
    testConnection()
    configure()
