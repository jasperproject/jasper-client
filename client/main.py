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

    # TODO: rename 'api_key' to 'google_stt_api_key'
    mic = Mic(speaker.newSpeaker(), PocketSphinxSTT(), stt.newSTTEngine(profile['api_key']))

    mic.say("How can I be of service?")

    conversation = Conversation("JASPER", mic, profile)

    conversation.handleForever()
