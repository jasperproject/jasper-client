#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import traceback
import wave
import json
import tempfile
import pkgutil
import logging
from abc import ABCMeta, abstractmethod
import requests
import yaml
import jasperpath

"""
The default Speech-to-Text implementation which relies on PocketSphinx.
"""

class TranscriptionMode:
    NORMAL, KEYWORD, MUSIC = range(3)

class AbstractSTTEngine(object):
    """
    Generic parent class for all STT engines
    """

    __metaclass__ = ABCMeta
    
    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    @abstractmethod
    def transcribe(self, fp, mode=TranscriptionMode.NORMAL):
        pass

class PocketSphinxSTT(AbstractSTTEngine):

    SLUG = 'sphinx'

    def __init__(self, lmd=jasperpath.config("languagemodel.lm"), dictd=jasperpath.config("dictionary.dic"),
                 lmd_persona=jasperpath.data("languagemodel_persona.lm"), dictd_persona=jasperpath.data("dictionary_persona.dic"),
                 lmd_music=None, dictd_music=None,
                 hmm_dir="/usr/local/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"):
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

        self._logfiles = {}
        with tempfile.NamedTemporaryFile(prefix='psdecoder_music_', suffix='.log', delete=False) as f:
            self._logfiles[TranscriptionMode.MUSIC] = f.name
        with tempfile.NamedTemporaryFile(prefix='psdecoder_keyword_', suffix='.log', delete=False) as f:
            self._logfiles[TranscriptionMode.KEYWORD] = f.name
        with tempfile.NamedTemporaryFile(prefix='psdecoder_normal_', suffix='.log', delete=False) as f:
            self._logfiles[TranscriptionMode.NORMAL] = f.name

        self._decoders = {}
        if lmd_music and dictd_music:
            self._decoders[TranscriptionMode.MUSIC] = ps.Decoder(hmm=hmm_dir, lm=lmd_music, dict=dictd_music, logfn=self._logfiles[TranscriptionMode.MUSIC])
        self._decoders[TranscriptionMode.KEYWORD]  = ps.Decoder(hmm=hmm_dir, lm=lmd_persona, dict=dictd_persona, logfn=self._logfiles[TranscriptionMode.KEYWORD])
        self._decoders[TranscriptionMode.NORMAL] = ps.Decoder(hmm=hmm_dir, lm=lmd, dict=dictd, logfn=self._logfiles[TranscriptionMode.NORMAL])

    def __del__(self):
        for filename in self._logfiles.values():
            os.remove(filename)

    @classmethod
    def get_config(cls): #FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = os.path.join(os.path.dirname(__file__), 'profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'pocketsphinx' in profile:
                    if 'hmm_dir' in profile['pocketsphinx']:
                        config['hmm_dir'] = profile['pocketsphinx']['hmm_dir']
                    if 'lmd' in profile['pocketsphinx']:
                        config['lmd'] = profile['pocketsphinx']['lmd']
                    if 'dictd' in profile['pocketsphinx']:
                        config['dictd'] = profile['pocketsphinx']['dictd']
                    if 'lmd_persona' in profile['pocketsphinx']:
                        config['lmd_persona'] = profile['pocketsphinx']['lmd_persona']
                    if 'dictd_persona' in profile['pocketsphinx']:
                        config['dictd_persona'] = profile['pocketsphinx']['dictd_persona']
                    if 'lmd_music' in profile['pocketsphinx']:
                        config['lmd'] = profile['pocketsphinx']['lmd_music']
                    if 'dictd_music' in profile['pocketsphinx']:
                        config['dictd_music'] = profile['pocketsphinx']['dictd_music']
        return config

    def transcribe(self, fp, mode=TranscriptionMode.NORMAL):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
        audio_file_path -- the path to the audio file to-be transcribed
        PERSONA_ONLY -- if True, uses the 'Persona' language model and dictionary
        MUSIC -- if True, uses the 'Music' language model and dictionary
        """
        decoder = self._decoders[mode]

        fp.seek(44)

        # FIXME: Can't use the Decoder.decode_raw() here, because
        # pocketsphinx segfaults with tempfile.SpooledTemporaryFile()
        data = fp.read()
        decoder.start_utt()
        decoder.process_raw(data, False, True)
        decoder.end_utt()
        
        result = decoder.get_hyp()
        with open(self._logfiles[mode], 'r+') as f:
                if mode == TranscriptionMode.KEYWORD:
                    modename = "[KEYWORD]"
                elif mode == TranscriptionMode.MUSIC:
                    modename = "[MUSIC]"
                else:
                    modename = "[NORMAL]"
                for line in f:
                    self._logger.debug("%s %s", modename, line.strip())
                f.truncate()

        print "==================="
        print "JASPER: " + result[0]
        print "==================="

        return [result[0]]

    @classmethod
    def is_available(cls):
        return (pkgutil.get_loader('pocketsphinx') is not None)

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

    def __init__(self, api_key=None): #FIXME: get init args from config
        """
        Arguments:
        api_key - the public api key which allows access to Google APIs
        """
        if not api_key:
            raise ValueError("No Google API Key given")
        self.api_key = api_key
        self.http = requests.Session()

    @classmethod
    def get_config(cls): #FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = os.path.join(os.path.dirname(__file__), 'profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'keys' in profile and 'GOOGLE_SPEECH' in profile['keys']:
                    config['api_key'] = profile['keys']['GOOGLE_SPEECH']
        return config

    def transcribe(self, fp, mode=TranscriptionMode.NORMAL):
        """
        Performs STT via the Google Speech API, transcribing an audio file and returning an English
        string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """

        wav = wave.open(fp, 'rb')
        frame_rate = wav.getframerate()
        wav.close()

        url = "https://www.google.com/speech-api/v2/recognize?output=json&client=chromium&key=%s&lang=%s&maxresults=6&pfilter=2" % (
            self.api_key, "en-us")

        data = fp.read()

        try:
            headers = {'Content-type': 'audio/l16; rate=%s' % frame_rate}
            response = self.http.post(url, data=data, headers=headers)
            response.encoding = 'utf-8'
            response_read = response.text

            response_parts = response_read.strip().split("\n")
            decoded = json.loads(response_parts[-1])
            if decoded['result']:
                texts = [alt['transcript'] for alt in decoded['result'][0]['alternative']]
                if texts:
                    print "==================="
                    print "JASPER: " + ', '.join(texts)
                    print "==================="
                return texts
            else:
                return []
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
        return engine(**engine.get_config())
