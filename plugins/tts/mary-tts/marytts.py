import logging
import urllib
import urlparse
import requests
from client import plugin


class MaryTTSPlugin(plugin.TTSPlugin):
    """
    Uses the MARY Text-to-Speech System (MaryTTS)
    MaryTTS is an open-source, multilingual Text-to-Speech Synthesis platform
    written in Java.
    Please specify your own server instead of using the demonstration server
    (http://mary.dfki.de:59125/) to save bandwidth and to protect your privacy.
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        self._logger = logging.getLogger(__name__)
        try:
            server = self.profile['mary-tts']['server']
        except KeyError:
            server = 'marytts.phonetik.uni-muenchen.de'
        self.server = server

        try:
            port = self.profile['mary-tts']['port']
        except KeyError:
            port = 59125
        self.port = port

        self.netloc = '{server}:{port}'.format(server=self.server,
                                               port=self.port)
        self.session = requests.Session()

        available_voices = self.get_voices()

        try:
            orig_language = self.profile['language']
        except:
            orig_language = 'en_US'

        language = orig_language.replace('-', '_')
        if language not in available_voices:
            language = language.split('_')[0]
        if language not in available_voices:
            raise ValueError("Language '%s' ('%s') not supported" %
                             (language, orig_language))
        self.language = language

        self._logger.info('Available voices:', ', '.join(
            available_voices[language]))

        try:
            voice = self.profile['mary-tts']['voice']
        except KeyError:
            voice = None

        if voice is not None and voice in available_voices[language]:
            self.voice = voice
        else:
            self.voice = available_voices[language][0]
            if voice is not None:
                self._logger.info("Voice '%s' not found, using '%s' instead.",
                                  voice, self.voice)

    def get_voices(self):
        voices = {}
        try:
            r = self.session.get(self._makeurl('/voices'))
            r.raise_for_status()
        except requests.exceptions.RequestException:
            self._logger.critical("Communication with MaryTTS server at %s " +
                                  "failed.", self.netloc)
            raise
        for line in r.text.splitlines():
            parts = line.strip().split()
            if len(parts) > 2:
                name = parts[0]
                lang = parts[1]
                if lang not in voices:
                    voices[lang] = []
                voices[lang].append(name)
        return voices

    def _makeurl(self, path, query={}):
        query_s = urllib.urlencode(query)
        urlparts = ('http', self.netloc, path, query_s, '')
        return urlparse.urlunsplit(urlparts)

    def say(self, phrase):
        query = {'OUTPUT_TYPE': 'AUDIO',
                 'AUDIO': 'WAVE_FILE',
                 'INPUT_TYPE': 'TEXT',
                 'INPUT_TEXT': phrase,
                 'LOCALE': self.language,
                 'VOICE': self.voice}

        r = self.session.get(self._makeurl('/process', query=query))
        return r.content
