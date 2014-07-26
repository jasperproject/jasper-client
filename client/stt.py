import os
import traceback
import json
import urllib2

"""
The default Speech-To-Text implementation which relies on PocketSphinx.
"""
class PocketSphinxSTT(object):

    def __init__(self, lmd = "languagemodel.lm", dictd = "dictionary.dic",
                lmd_persona = "languagemodel_persona.lm", dictd_persona = "dictionary_persona.dic",
                lmd_music=None, dictd_music=None):
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
            self.speechRec_music = ps.Decoder(hmm = hmdir, lm = lmd_music, dict = dictd_music)
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
5. Copy your API key and run client/populate.py. When prompted, paste this key for access to the Speech API.

This implementation also requires that the avconv audio utility be present on your $PATH. On RPi, simply run:
    sudo apt-get install avconv
"""
class GoogleSTT(object):

    RATE = 44100

    def __init__(self, api_key):
        """
        Arguments:
        api_key - the public api key which allows access to Google APIs
        """

        self.api_key = api_key
        for tool in ("avconv", "ffmpeg"):
            if os.system("which %s" % tool) == 0:
                self.audio_tool = tool
                break  
        if not self.audio_tool:
            raise Exception("Could not find an audio tool to convert .wav files to .flac")

    def transcribe(self, audio_file_path):
        """
            Performs STT via the Google Speech API, transcribing an audio file 
            and returning an English string.
            audio_file_path -- the path to the audio file to-be transcribed

        """
        AUDIO_FILE_FLAC = "active.flac"
        os.system("%s -y -i %s -f flac -b:a 44100 %s" % (self.audio_tool, audio_file_path, AUDIO_FILE_FLAC))

        url = "https://www.google.com/speech-api/v2/recognize?output=json&client=chromium&key=%s&lang=%s&maxresults=6&pfilter=2" % (self.api_key, "en-us")
        flac = open(AUDIO_FILE_FLAC, 'rb')
        data = flac.read()
        flac.close()
        try:
            req = urllib2.Request(
                url,
                data=data,
                headers={
                    'Content-type': 'audio/x-flac; rate=%s' % GoogleSTT.RATE})
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

If api_key is not supplied, Jasper will rely on the PocketSphinx STT engine for
audio transcription.

If api_key is supplied, Jasper will use the Google Speech API for transcribing
audio while in the active listen phase. Jasper will continue to rely on the
PocketSphinx engine during the passive listen phase, as the Google Speech API 
is rate limited to 50 requests/day.

Arguments:
api_key - if supplied, Jasper will use the Google Speech API for transcribing
audio in the active listen phase.

"""
def newSTTEngine(api_key = None):
    if api_key:
        return GoogleSTT(api_key)
    else:
        return PocketSphinxSTT()
