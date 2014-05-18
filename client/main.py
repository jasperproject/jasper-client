import yaml
import sys
from conversation import Conversation


def isLocal():
    return len(sys.argv) > 1 and sys.argv[1] == "--local"

if isLocal():
    from input.text import Receiver as Receiver
    from output.text import Sender as Sender
else:
    from input.att_audio import Receiver as Receiver
    from output.att_audio import Sender as Sender

if __name__ == "__main__":

    print "==========================================================="
    print " JASPER The Talking Computer                               "
    print " Copyright 2013 Shubhro Saha & Charlie Marsh               "
    print "==========================================================="

    profile = yaml.safe_load(open("profile.yml", "r"))

    receiver = Receiver("languagemodel.lm", "dictionary.dic",
              "languagemodel_persona.lm", "dictionary_persona.dic")

    sender = Sender()

    sender.say("How can I be of service?")

    conversation = Conversation("JASPER", sender, receiver, profile)

    conversation.handleForever()
