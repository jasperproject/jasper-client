#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
import traceback
import wave
import json
import tempfile
import logging
from abc import ABCMeta, abstractmethod
import requests
import yaml
import jasperpath
import diagnose
import vocabcompiler


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
    """
    The default Speech-to-Text implementation which relies on PocketSphinx.
    """

    SLUG = 'sphinx'

    def __init__(self, vocabulary=None, vocabulary_keyword=None,
                 vocabulary_music=None, hmm_dir="/usr/local/share/" +
                 "pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"):

        """
        Initiates the pocketsphinx instance.

        Arguments:
            vocabulary -- a PocketsphinxVocabulary instance
            vocabulary_keyword -- a PocketsphinxVocabulary instance
                                  (containing, e.g., 'Jasper')
            vocabulary_music -- (optional) a PocketsphinxVocabulary instance
            hmm_dir -- the path of the Hidden Markov Model (HMM)
        """

        self._logger = logging.getLogger(__name__)

        # quirky bug where first import doesn't work
        try:
            import pocketsphinx as ps
        except:
            import pocketsphinx as ps

        self._logfiles = {}
        with tempfile.NamedTemporaryFile(prefix='psdecoder_music_',
                                         suffix='.log', delete=False) as f:
            self._logfiles[TranscriptionMode.MUSIC] = f.name
        with tempfile.NamedTemporaryFile(prefix='psdecoder_keyword_',
                                         suffix='.log', delete=False) as f:
            self._logfiles[TranscriptionMode.KEYWORD] = f.name
        with tempfile.NamedTemporaryFile(prefix='psdecoder_normal_',
                                         suffix='.log', delete=False) as f:
            self._logfiles[TranscriptionMode.NORMAL] = f.name

        self._decoders = {}
        if vocabulary_music is not None:
            self._decoders[TranscriptionMode.MUSIC] = \
                ps.Decoder(hmm=hmm_dir,
                           logfn=self._logfiles[TranscriptionMode.MUSIC],
                           **vocabulary_music.decoder_kwargs)
        self._decoders[TranscriptionMode.KEYWORD] = \
            ps.Decoder(hmm=hmm_dir,
                       logfn=self._logfiles[TranscriptionMode.KEYWORD],
                       **vocabulary_keyword.decoder_kwargs)
        self._decoders[TranscriptionMode.NORMAL] = \
            ps.Decoder(hmm=hmm_dir,
                       logfn=self._logfiles[TranscriptionMode.NORMAL],
                       **vocabulary.decoder_kwargs)

    def __del__(self):
        for filename in self._logfiles.values():
            os.remove(filename)

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = os.path.join(os.path.dirname(__file__), 'profile.yml')

        name_default = 'default'
        path_default = jasperpath.config('vocabularies')

        name_keyword = 'keyword'
        path_keyword = jasperpath.config('vocabularies')

        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'pocketsphinx' in profile:
                    if 'hmm_dir' in profile['pocketsphinx']:
                        config['hmm_dir'] = profile['pocketsphinx']['hmm_dir']

                    if 'vocabulary_default_name' in profile['pocketsphinx']:
                        name_default = \
                            profile['pocketsphinx']['vocabulary_default_name']

                    if 'vocabulary_default_path' in profile['pocketsphinx']:
                        path_default = \
                            profile['pocketsphinx']['vocabulary_default_path']

                    if 'vocabulary_keyword_name' in profile['pocketsphinx']:
                        name_keyword = \
                            profile['pocketsphinx']['vocabulary_keyword_name']

                    if 'vocabulary_keyword_path' in profile['pocketsphinx']:
                        path_keyword = \
                            profile['pocketsphinx']['vocabulary_keyword_path']

        config['vocabulary'] = vocabcompiler.PocketsphinxVocabulary(
            name_default, path=path_default)
        config['vocabulary_keyword'] = vocabcompiler.PocketsphinxVocabulary(
            name_keyword, path=path_keyword)

        config['vocabulary'].compile(vocabcompiler.get_all_phrases())
        config['vocabulary_keyword'].compile(
            vocabcompiler.get_keyword_phrases())

        return config

    def transcribe(self, fp, mode=TranscriptionMode.NORMAL):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
        audio_file_path -- the path to the audio file to-be transcribed
        PERSONA_ONLY -- if True, uses the 'Persona' language model and
                        dictionary
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
        return diagnose.check_python_import('pocketsphinx')


class GoogleSTT(AbstractSTTEngine):
    """
    Speech-To-Text implementation which relies on the Google Speech API.

    This implementation requires a Google API key to be present in profile.yml

    To obtain an API key:
    1. Join the Chromium Dev group:
       https://groups.google.com/a/chromium.org/forum/?fromgroups#!forum/chromium-dev
    2. Create a project through the Google Developers console:
       https://console.developers.google.com/project
    3. Select your project. In the sidebar, navigate to "APIs & Auth." Activate
       the Speech API.
    4. Under "APIs & Auth," navigate to "Credentials." Create a new key for
       public API access.
    5. Add your credentials to your profile.yml. Add an entry to the 'keys'
       section using the key name 'GOOGLE_SPEECH.' Sample configuration:
    6. Set the value of the 'stt_engine' key in your profile.yml to 'google'


    Excerpt from sample profile.yml:

        ...
        timezone: US/Pacific
        stt_engine: google
        keys:
            GOOGLE_SPEECH: $YOUR_KEY_HERE

    """

    SLUG = 'google'

    def __init__(self, api_key=None):
        # FIXME: get init args from config
        """
        Arguments:
        api_key - the public api key which allows access to Google APIs
        """
        if not api_key:
            raise ValueError("No Google API Key given")
        self.api_key = api_key
        self.http = requests.Session()

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
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
        Performs STT via the Google Speech API, transcribing an audio file and
        returning an English string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """

        wav = wave.open(fp, 'rb')
        frame_rate = wav.getframerate()
        wav.close()

        url = (("https://www.google.com/speech-api/v2/recognize?output=json" +
                "&client=chromium&key=%s&lang=%s&maxresults=6&pfilter=2") %
               (self.api_key, "en-us"))

        data = fp.read()

        try:
            headers = {'Content-type': 'audio/l16; rate=%s' % frame_rate}
            response = self.http.post(url, data=data, headers=headers)
            response.encoding = 'utf-8'
            response_read = response.text

            response_parts = response_read.strip().split("\n")
            decoded = json.loads(response_parts[-1])
            if decoded['result']:
                texts = [alt['transcript'] for alt in
                         decoded['result'][0]['alternative']]
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
        return diagnose.check_network_connection()


def get_engines():
    return [stt_engine for stt_engine in AbstractSTTEngine.__subclasses__()
            if hasattr(stt_engine, 'SLUG') and stt_engine.SLUG]


def newSTTEngine(stt_engine, **kwargs):
    """
    Returns a Speech-To-Text engine.

    Currently, the supported implementations are the default Pocket Sphinx and
    the Google Speech API

    Arguments:
        engine_type -- one of "sphinx" or "google"
        kwargs -- keyword arguments passed to the constructor of the STT engine
    """
    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == stt_engine, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No STT engine found for slug '%s'" % stt_engine)
    else:
        if len(selected_engines) > 1:
            print(("WARNING: Multiple STT engines found for slug '%s'. This " +
                   "is most certainly a bug.") % stt_engine)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("STT engine '%s' is not available (due to " +
                              "missing dependencies, missing dependencies, " +
                              "etc.)") % stt_engine)
        return engine(**engine.get_config())
