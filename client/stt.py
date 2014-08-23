import traceback
import json
import urllib2

"""
The default Speech-to-Text implementation which relies on PocketSphinx.
"""


class PocketSphinxSTT(object):

    def __init__(self, lmd="languagemodel.lm", dictd="dictionary.dic",
                 lmd_persona="languagemodel_persona.lm", dictd_persona="dictionary_persona.dic",
                 lmd_music=None, dictd_music=None, **kwargs):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        lmd -- filename of the full language model
        dictd -- filename of the full dictionary (.dic)
        lmd_persona -- filename of the 'Persona' language model (containing, e.g., 'Jasper')
        dictd_persona -- filename of the 'Persona' dictionary (.dic)
        """

        # quirky bug where first import doesn't work
        try:
            import pocketsphinx as ps
        except:
            import pocketsphinx as ps

        hmdir = "/usr/local/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"

        if lmd_music and dictd_music:
            self.speechRec_music = ps.Decoder(hmm=hmdir, lm=lmd_music, dict=dictd_music)
        self.speechRec_persona = ps.Decoder(
            hmm=hmdir, lm=lmd_persona, dict=dictd_persona)
        self.speechRec = ps.Decoder(hmm=hmdir, lm=lmd, dict=dictd)

    def transcribe(self, audio_file_path, PERSONA_ONLY=False, MUSIC=False):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
        audio_file_path -- the path to the audio file to-be transcribed
        PERSONA_ONLY -- if True, uses the 'Persona' language model and dictionary
        MUSIC -- if True, uses the 'Music' language model and dictionary
        """

        wavFile = file(audio_file_path, 'rb')
        wavFile.seek(44)

        if MUSIC:
            self.speechRec_music.decode_raw(wavFile)
            result = self.speechRec_music.get_hyp()
        elif PERSONA_ONLY:
            self.speechRec_persona.decode_raw(wavFile)
            result = self.speechRec_persona.get_hyp()
        else:
            self.speechRec.decode_raw(wavFile)
            result = self.speechRec.get_hyp()

        print "==================="
        print "JASPER: " + result[0]
        print "==================="

        return result[0]

"""
Speech-To-Text implementation which relies on the Google Speech API.

This implementation requires a Google API key to be present in profile.yml

To obtain an API key:
1. Join the Chromium Dev group: https://groups.google.com/a/chromium.org/forum/?fromgroups#!forum/chromium-dev
2. Create a project through the Google Developers console: https://console.developers.google.com/project
3. Select your project. In the sidebar, navigate to "APIs & Auth." Activate the Speech API.
4. Under "APIs & Auth," navigate to "Credentials." Create a new key for public API access.
5. Add your credentials to your profile.yml. Add an entry to the 'keys' section using the key name 'GOOGLE_SPEECH.' Sample configuration:
6. Set the value of the 'stt_engine' key in your profile.yml to 'google'


Excerpt from sample profile.yml:

    ...
    timezone: US/Pacific
    stt_engine: google
    keys:
        GOOGLE_SPEECH: $YOUR_KEY_HERE

"""


class GoogleSTT(object):

    RATE = 16000

    def __init__(self, api_key, **kwargs):
        """
        Arguments:
        api_key - the public api key which allows access to Google APIs
        """
        self.api_key = api_key

    def transcribe(self, audio_file_path, PERSONA_ONLY=False, MUSIC=False):
        """
        Performs STT via the Google Speech API, transcribing an audio file and returning an English
        string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """
        url = "https://www.google.com/speech-api/v2/recognize?output=json&client=chromium&key=%s&lang=%s&maxresults=6&pfilter=2" % (
            self.api_key, "en-us")

        wav = open(audio_file_path, 'rb')
        data = wav.read()
        wav.close()

        try:
            req = urllib2.Request(
                url,
                data=data,
                headers={
                    'Content-type': 'audio/l16; rate=%s' % GoogleSTT.RATE})
            response_url = urllib2.urlopen(req)
            response_read = response_url.read()
            response_read = response_read.decode('utf-8')
            decoded = json.loads(response_read.split("\n")[1])
            print response_read
            text = decoded['result'][0]['alternative'][0]['transcript']
            if text:
                print "==================="
                print "JASPER: " + text
                print "==================="
            return text
        except Exception:
            traceback.print_exc()

"""
Returns a Speech-To-Text engine.

Currently, the supported implementations are the default Pocket Sphinx and
the Google Speech API

Arguments:
engine_type - one of "sphinx" or "google"
kwargs - keyword arguments passed to the constructor of the STT engine
"""


def newSTTEngine(engine_type, **kwargs):
    t = engine_type.lower()
    if t == "sphinx":
        return PocketSphinxSTT(**kwargs)
    elif t == "google":
        return GoogleSTT(**kwargs)
    else:
        raise ValueError("Unsupported STT engine type: " + engine_type)
