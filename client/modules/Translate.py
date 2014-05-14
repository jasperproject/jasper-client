import re
#from mic import langCode

WORDS = ["TRANSLATE"]

#langCode = mic.langCode

def handle(text, mic, profile):
    mic.say("Okay.")
    google_text = mic.activeListen(GOOGLE=True)
    if google_text == "no_info":
        mic.say("Google did not catch that, could you please repeat.")
        google_text = mic.activeListen(GOOGLE=True)
        if google_text == "no":
            mic.say("Ok, please try again later")
        elif google_text == "no_info":
            mic.say("Google did not catch that again, please try again later.")
        else:
            mic.say(google_text, translate=True)        
    else:
        mic.say(google_text, translate=True)

def isValid(text):
    return bool(re.search(r'\btranslate\b', text, re.IGNORECASE))
