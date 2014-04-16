import re

WORDS = ["TEST"]

def handle(text, mic, profile):
    mic.say("Say something to test the A.P.I. I will then say it back.")
    google_text = mic.activeListen(GOOGLE=True)
    if google_text == "no_info":
        mic.say("Google did not catch that, yould you please repeat.")
        google_text = mic.activeListen(GOOGLE=True)
        if google_text == "no":
            mic.say("Ok, please try again later")
        elif google_text == "no_info":
            mic.say("Google did not catch that again, please try again later.")
        else:
            mic.say(google_text)        
    else:
        mic.say(google_text)

def isValid(text):
    return bool(re.search(r'\btest\b', text, re.IGNORECASE))

