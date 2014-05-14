import re
import os
import subprocess

WORDS = ["WEMO", "TURN", "ON", "OFF", "ALL", "SWITCH"]

output = subprocess.check_output("wemo list | awk '{gsub(/Switch: /,\"\",$0); print $0}'", shell=True).splitlines()
newwords = "[ \"%s\" ]" % " ".join(output).upper().replace(" ","\", \"")

WORDS.extend(eval(newwords))

def handle(text, mic, profile):
    """
        Controls the WeMo switches.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """
#    if bool(re.search(r'\bon\b', text, re.IGNORECASE)):
#	response = "on"
#    else:
#	response = "off"
#    mic.say("Turning %s %s." % (action, switch)
#    os.system("wemo switch FloorLamp %s" % action)
    search_value = re.findall(r'\b\S+\b' , text.upper())
    exclude = [ "LIGHT", "LIGHTS", "SWITCH", "SWITCHES", "LAMP", "LAMPS" ]
    search_value = [ unique for unique in search_value if unique not in exclude ]
    for list in output:
	if any( item for item in search_value if item in list.upper() ):
		if "ON" in [ words for words in search_value ]:
			action = "on"
		elif "OFF" in [ words for words in search_value ]:
			action = "off"
		else:
			mic.say("Please try again.")
			break
		mic.say("Turning %s %s." % (action, output[output.index(list)]))
		os.system("wemo switch \"%s\" %s" % (output[output.index(list)], action))
		break
	elif ( "ALL" in search_value ):
		if "ON" in search_value:
			action = "on"
		elif "OFF" in search_value:
			action = "off"
		else:
			mic.say("Please try again.")
			break
		mic.say("Turning all switches %s" % action)
		for switch in output:
			os.system("wemo switch \"%s\" %s" % (switch, action))
		break


def isValid(text):
    """
        Returns True if input is related to wemo or lights.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(turn|wemo)\b', text, re.IGNORECASE))
