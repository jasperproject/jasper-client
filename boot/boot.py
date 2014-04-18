#!/usr/bin/env python

import os, json
import urllib2
import subprocess
import yaml
from wifi import *
from time import sleep
import vocabcompiler

def say(phrase, OPTIONS = " -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):

    os.system("espeak " + json.dumps(phrase) + OPTIONS)
    os.system("aplay -D hw:0,0 say.wav")



# check if there is network connection
def configure(tryNum):
    try:

        urllib2.urlopen("http://www.google.com").getcode()

        print "CONNECTED TO INTERNET"
        print "COMPILING DICTIONARY"
        vocabcompiler.compile()

        print "STARTING CLIENT PROGRAM"

        try:
            os.system("$HOME/jasper/client/start.sh &")
        except:
            os.system("$HOME/jasper/backup/start.sh &")
        finally:
            return

    except:

	if tryNum == 1:
		return

        networks = yaml.safe_load(open("networks.yml", "r"))

        wifi = Wifi()

        for network in networks:
            wifi.set_default_wifi(network['SSID'], network['KEY'])
            say("Attempting to connect to network " + network['SSID'])

            try:

                urllib2.urlopen("http://www.google.com").getcode()

                print "CONNECTED TO INTERNET"
                print "COMPILING DICTIONARY"
                vocabcompiler.compile()

                print "STARTING CLIENT PROGRAM"

                try:
                    os.system("$HOME/jasper/client/start.sh &")
                except:
                    os.system("$HOME/jasper/backup/start.sh &")
                finally:
                    return

            except:
                pass

        print "NOT CONNECTED TO INTERNET. RUNNING AD HOC NETWORK."

        wifi.setup_adhoc()

        os.system("sudo app/app.sh &")
        say("Hello.... I could not connect to a wifi network... Please log in with your computer to help me")

        original = open("networks.yml",'r').readlines()
        while True:
            list = open("networks.yml",'r').readlines()
            if list != original:
                break

        say("Thank you for adding a wifi network. Just give me a few minutes to restart.")
        os.system("sudo shutdown -r now")

if __name__ == "__main__":
    print "==========STARTING JASPER CLIENT=========="
    print "=========================================="
    print "COPYRIGHT 2013 SHUBHRO SAHA, CHARLIE MARSH"
    print "=========================================="
    say("Hello.... I am Jasper... Please wait one moment.")
    configure(1)
    sleep(60)
    configure(2)
