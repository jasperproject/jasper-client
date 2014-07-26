import yaml
import sys
import speaker
import stt
from stt import PocketSphinxSTT
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

    profile = yaml.safe_load(open("profile.yml", "r"))

    try:
        google_api_key = profile['google_api_key']
    except KeyError:
        print "Google STT API Key not present in profile - defaulting to PocketSphinx..."
        google_api_key = None

    mic = Mic(speaker.newSpeaker(), PocketSphinxSTT(), stt.newSTTEngine(google_api_key))

    mic.say("How can I be of service?")

    conversation = Conversation("JASPER", mic, profile)

    conversation.handleForever()
