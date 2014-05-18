__author__ = 'seanfitz'
import alteration
import json
import os
import requests
import yaml
import sys
import pyaudio
import wave
import time
profile = yaml.safe_load(open("profile.yml", "r"))


def get_att_auth_token(client_id, client_secret):
    response = requests.post('https://api.att.com/oauth/token',
                  headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'},
                  data={'client_id': client_id, 'client_secret': client_secret, 'scope':'SPEECH,TTS', 'grant_type':'client_credentials'})
    return response.json()

class Sender(object):
    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)
        auth_token = get_att_auth_token(profile.get('att_api_client_id'), profile.get('att_api_client_secret'))
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=16000,
                        output=True)

        response = requests.post('https://api.att.com/speech/v3/textToSpeech',
                                headers={'Accept': 'audio/x-wav', 'Content-Length': sys.getsizeof(phrase),
                                         'Content-Type': 'text/plain',
                                         'Authorization': 'Bearer %s' % auth_token.get('access_token')},
                                data=phrase, stream=True)
        if not response.ok:
            # fall back onto espeak
            print(response.text)
            os.system("espeak " + json.dumps(phrase) + OPTIONS)
            os.system("aplay -D hw:1,0 say.wav")
        else:
            for block in response.iter_content(1024):
                if not block:
                    break

                stream.write(block)

        # sleep for .5 seconds to allow stream to complete
        time.sleep(.5)

        stream.stop_stream()
        stream.close()

        p.terminate()

if __name__ == "__main__":
    sender = Sender()
    sender.say('Testing ATT speech recognition.')
