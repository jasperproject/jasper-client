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


class AbstractSTTEngine(object):
    """
    Generic parent class for all STT engines
    """

    __metaclass__ = ABCMeta
    VOCABULARY_TYPE = None

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls, vocabulary_name, phrases):
        config = cls.get_config()
        if cls.VOCABULARY_TYPE:
            vocabulary = cls.VOCABULARY_TYPE(vocabulary_name,
                                             path=jasperpath.config(
                                                 'vocabularies'))
            if not vocabulary.matches_phrases(phrases):
                vocabulary.compile(phrases)
            config['vocabulary'] = vocabulary
        instance = cls(**config)
        return instance

    @classmethod
    def get_passive_instance(cls):
        phrases = vocabcompiler.get_keyword_phrases()
        return cls.get_instance('keyword', phrases)

    @classmethod
    def get_active_instance(cls):
        phrases = vocabcompiler.get_all_phrases()
        return cls.get_instance('default', phrases)

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    @abstractmethod
    def transcribe(self, fp):
        pass


class PocketSphinxSTT(AbstractSTTEngine):
    """
    The default Speech-to-Text implementation which relies on PocketSphinx.
    """

    SLUG = 'sphinx'
    VOCABULARY_TYPE = vocabcompiler.PocketsphinxVocabulary

    def __init__(self, vocabulary, hmm_dir="/usr/local/share/" +
                 "pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"):

        """
        Initiates the pocketsphinx instance.

        Arguments:
            vocabulary -- a PocketsphinxVocabulary instance
            hmm_dir -- the path of the Hidden Markov Model (HMM)
        """

        self._logger = logging.getLogger(__name__)

        # quirky bug where first import doesn't work
        try:
            import pocketsphinx as ps
        except:
            import pocketsphinx as ps

        with tempfile.NamedTemporaryFile(prefix='psdecoder_',
                                         suffix='.log', delete=False) as f:
            self._logfile = f.name

        self._decoder = ps.Decoder(hmm=hmm_dir, logfn=self._logfile,
                                   **vocabulary.decoder_kwargs)

    def __del__(self):
        os.remove(self._logfile)

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = jasperpath.config('profile.yml')

        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                try:
                    config['hmm_dir'] = profile['pocketsphinx']['hmm_dir']
                except KeyError:
                    pass

        return config

    def transcribe(self, fp):
        """
        Performs STT, transcribing an audio file and returning the result.

        Arguments:
            fp -- a file object containing audio data
        """

        fp.seek(44)

        # FIXME: Can't use the Decoder.decode_raw() here, because
        # pocketsphinx segfaults with tempfile.SpooledTemporaryFile()
        data = fp.read()
        self._decoder.start_utt()
        self._decoder.process_raw(data, False, True)
        self._decoder.end_utt()

        result = self._decoder.get_hyp()
        with open(self._logfile, 'r+') as f:
            for line in f:
                self._logger.debug(line.strip())
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
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'keys' in profile and 'GOOGLE_SPEECH' in profile['keys']:
                    config['api_key'] = profile['keys']['GOOGLE_SPEECH']
        return config

    def transcribe(self, fp):
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


class ATandTSTT(AbstractSTTEngine):

    SLUG = "att"

    def __init__(self, app_key, app_secret):
        self._logger = logging.getLogger(__name__)
        self._token = None
        self.app_key = app_key
        self.app_secret = app_secret

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # HMM dir
        # Try to get hmm_dir from config
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'att-stt' in profile:
                    if 'app_key' in profile['att-stt']:
                        config['app_key'] = profile['att-stt']['app_key']
                    if 'app_secret' in profile['att-stt']:
                        config['app_secret'] = profile['att-stt']['app_secret']
        return config

    @property
    def token(self):
        if not self._token:
            headers = {'content-type': 'application/x-www-form-urlencoded',
                       'accept': 'application/json'}
            payload = {'client_id': self.app_key,
                       'client_secret': self.app_secret,
                       'scope': 'SPEECH',
                       'grant_type': 'client_credentials'}
            r = requests.post('https://api.att.com/oauth/token',
                              data=payload,
                              headers=headers)
            self._token = r.json()['access_token']
        return self._token

    def transcribe(self, fp):
        data = fp.read()
        r = self._get_response(data)
        if r.status_code == requests.codes['unauthorized']:
            # Request token invalid, retry once with a new token
            self._logger.warning('OAuth access token invalid, generating a ' +
                                 'new one and retrying...')
            self._token = None
            r = self._get_response(data)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return []
        except requests.exceptions.RequestException:
            self._logger.critical('Request failed.', exc_info=True)
            return []
        else:
            try:
                recognition = r.json()['Recognition']
                if recognition['Status'] != 'OK':
                    raise ValueError(recognition['Status'])
                results = [(x['Hypothesis'], x['Confidence'])
                           for x in recognition['NBest']]
            except ValueError as e:
                self._logger.debug('Recognition failed with status: %s',
                                   e.args[0])
                return []
            except KeyError:
                self._logger.critical('Cannot parse response.',
                                      exc_info=True)
                return []
            else:
                results = [x[0].upper() for x in sorted(results,
                                                        key=lambda x: x[1],
                                                        reverse=True)]
                self._logger.info('Recognized: %r', results)
                return results

    def _get_response(self, data):
        headers = {'authorization': 'Bearer %s' % self.token,
                   'accept': 'application/json',
                   'content-type': 'audio/wav'}
        return requests.post('https://api.att.com/speech/v3/speechToText',
                             data=data,
                             headers=headers)

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()


def get_engine_by_slug(slug=None):
    """
    Returns:
        An STT Engine implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No TTS engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print("WARNING: Multiple TTS engines found for slug '%s'. " +
                  "This is most certainly a bug." % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError("TTS engine '%s' is not available (due to " +
                             "missing dependencies, missing " +
                             "dependencies, etc.)" % slug)
        return engine


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [tts_engine for tts_engine in
            list(get_subclasses(AbstractSTTEngine))
            if hasattr(tts_engine, 'SLUG') and tts_engine.SLUG]
