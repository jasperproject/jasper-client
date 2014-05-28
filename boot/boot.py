#!/usr/bin/env python

import os, json
import urllib2
import yaml

import vocabcompiler

def say(phrase, OPTIONS = " -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
    os.system("espeak " + json.dumps(phrase) + OPTIONS)
    os.system("aplay -D hw:1,0 say.wav")

def configure():
    try:
        urllib2.urlopen("http://www.google.com").getcode()

        print "CONNECTED TO INTERNET"
        print "COMPILING DICTIONARY"
        vocabcompiler.compile("../client/sentences.txt", "../client/dictionary.dic", "../client/languagemodel.lm")

        print "STARTING CLIENT PROGRAM"
        os.system("/home/pi/jasper/client/start.sh &")
        
    except:
        
        print "COULD NOT CONNECT TO NETWORK"
        say("Hello, I could not connect to a network. Please read the documentation to configure your Raspberry Pi.")
        #os.system("sudo shutdown -r now")

if __name__ == "__main__":
    print "==========STARTING JASPER CLIENT=========="
    print "=========================================="
    print "COPYRIGHT 2013 SHUBHRO SAHA, CHARLIE MARSH"
    print "=========================================="
    say("Hello.... I am Jasper... Please wait one moment.")
    configure()
