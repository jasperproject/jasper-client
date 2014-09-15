#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import traceback
import json
import tempfile
import logging
from abc import ABCMeta, abstractmethod
import requests
import yaml

"""
The default Speech-to-Text implementation which relies on PocketSphinx.
"""

class AbstractSTTEngine(object):
    """
    Generic parent class for all STT engines
    """

    __metaclass__ = ABCMeta
    
    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    @abstractmethod
    def transcribe(self, audio_file_path, PERSONA_ONLY=False, MUSIC=False):
        pass

class PocketSphinxSTT(AbstractSTTEngine):

    SLUG = 'sphinx'

    def __init__(self, lmd="languagemodel.lm", dictd="dictionary.dic",
                 lmd_persona="languagemodel_persona.lm", dictd_persona="dictionary_persona.dic",
                 lmd_music=None, dictd_music=None, **kwargs): #FIXME: get init args from config
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        lmd -- filename of the full language model
        dictd -- filename of the full dictionary (.dic)
        lmd_persona -- filename of the 'Persona' language model (containing, e.g., 'Jasper')
        dictd_persona -- filename of the 'Persona' dictionary (.dic)
        """

        self._logger = logging.getLogger(__name__)

        # quirky bug where first import doesn't work
        try:
            import pocketsphinx as ps
        except:
            import pocketsphinx as ps

        hmm_dir = self._get_hmm_dir()

        with tempfile.NamedTemporaryFile(prefix='psdecoder_music_', suffix='.log', delete=False) as f:
            self.logfile_music = f.name
        with tempfile.NamedTemporaryFile(prefix='psdecoder_persona_', suffix='.log', delete=False) as f:
            self.logfile_persona = f.name
        with tempfile.NamedTemporaryFile(prefix='psdecoder_default_', suffix='.log', delete=False) as f:
            self.logfile_default = f.name

        if lmd_music and dictd_music:
            self.speechRec_music = ps.Decoder(hmm=hmm_dir, lm=lmd_music, dict=dictd_music, logfn=self.logfile_music)
        self.speechRec_persona = ps.Decoder(
            hmm=hmm_dir, lm=lmd_persona, dict=dictd_persona, logfn=self.logfile_persona)
        self.speechRec = ps.Decoder(hmm=hmm_dir, lm=lmd, dict=dictd, logfn=self.logfile_default)

    def __del__(self):
        os.remove(self.logfile_music)
        os.remove(self.logfile_persona)
        os.remove(self.logfile_default)

    @classmethod
    def _get_hmm_dir(cls): #FIXME: Replace this as soon as we have a config module
        hmm_dir = None

        # Try to get hmm_dir from config
        profile_path = os.path.join(os.path.dirname(__file__), 'profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'pocketsphinx' in profile and 'hmm_dir' in profile['pocketsphinx']:
                    hmm_dir = profile['pocketsphinx']['hmm_dir']

        if not hmm_dir:
            hmm_dir = "/usr/local/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"

        return hmm_dir

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
            with open(self.logfile_music, 'r+') as f:
                for line in f:
                    self._logger.debug("speechRec_music %s", line.strip())
                f.truncate()
        elif PERSONA_ONLY:
            self.speechRec_persona.decode_raw(wavFile)
            result = self.speechRec_persona.get_hyp()
            with open(self.logfile_persona, 'r+') as f:
                for line in f:
                    self._logger.debug("speechRec_persona %s", line.strip())
                f.truncate()
        else:
            self.speechRec.decode_raw(wavFile)
            result = self.speechRec.get_hyp()
            with open(self.logfile_default, 'r+') as f:
                for line in f:
                    self._logger.debug("speechRec_default %s", line.strip())
                f.truncate()

        print "==================="
        print "JASPER: " + result[0]
        print "==================="

        return result[0]

    @classmethod
    def is_available(cls):
        return (pkgutil.get_loader('pocketsphinx') is not None and os.path.exits(cls._get_hmm_dir()))

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


class GoogleSTT(AbstractSTTEngine):

    SLUG = 'google'
    RATE = 16000

    def __init__(self, api_key=None, **kwargs): #FIXME: get init args from config
        """
        Arguments:
        api_key - the public api key which allows access to Google APIs
        """
        self.api_key = api_key
        self.http = requests.Session()

    def transcribe(self, audio_file_path, PERSONA_ONLY=False, MUSIC=False):
        """
        Performs STT via the Google Speech API, transcribing an audio file and returning an English
        string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """
        url = "https://www.google.com/speech-api/v2/recognize?output=json&client=chromium&key=%s&lang=%s&maxresults=6&pfilter=2" % (
            self.api_key, "en-us")

        with open(audio_file_path, 'rb') as f:
            data = f.read()

        try:
            headers = {'Content-type': 'audio/l16; rate=%s' % GoogleSTT.RATE}
            response = self.http.post(url, data=data, headers=headers)
            response.encoding = 'utf-8'
            response_read = response.text
            decoded = json.loads(response_read.split("\n")[1])

            text = decoded['result'][0]['alternative'][0]['transcript']
            if text:
                print "==================="
                print "JASPER: " + text
                print "==================="
            return text
        except Exception:
            traceback.print_exc()

    @classmethod
    def is_available(cls):
        return True

"""
Returns a Speech-To-Text engine.

Currently, the supported implementations are the default Pocket Sphinx and
the Google Speech API

Arguments:
engine_type - one of "sphinx" or "google"
kwargs - keyword arguments passed to the constructor of the STT engine
"""
def get_engines():
    return [stt_engine for stt_engine in AbstractSTTEngine.__subclasses__() if hasattr(stt_engine, 'SLUG') and stt_engine.SLUG]

def newSTTEngine(stt_engine, **kwargs):
    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and engine.SLUG == stt_engine, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No STT engine found for slug '%s'" % stt_engine)
    else:
        if len(selected_engines) > 1:
            print("WARNING: Multiple STT engines found for slug '%s'. This is most certainly a bug." % stt_engine)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError("STT engine '%s' is not available (due to missing dependencies, missing dependencies, etc.)" % stt_engine)
        return engine(**kwargs)
