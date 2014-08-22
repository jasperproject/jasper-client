import yaml
import sys
import speaker
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

    mic = Mic(speaker.newSpeaker(), stt.PocketSphinxSTT(),
              stt.newSTTEngine(stt_engine_type, api_key=api_key))

    addendum = ""
    if 'first_name' in profile:
        addendum = ", %s" % profile["first_name"]
    mic.say("How can I be of service%s?" % addendum)

    conversation = Conversation("JASPER", mic, profile)

    conversation.handleForever()
