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
            server = 'mary.dfki.de'
        self.server = server

        try:
            port = self.profile['mary-tts']['port']
        except KeyError:
            port = 59125
        self.port = port

        try:
            voice = self.profile['mary-tts']['voice']
        except KeyError:
            voice = "dfki-spike"
        self.voice = voice

        self.language = 'en_GB'  # FIXME

        self.netloc = '{server}:{port}'.format(server=self.server,
                                               port=self.port)
        self.session = requests.Session()

    @property
    def languages(self):
        try:
            r = self.session.get(self._makeurl('/locales'))
            r.raise_for_status()
        except requests.exceptions.RequestException:
            self._logger.critical("Communication with MaryTTS server at %s " +
                                  "failed.", self.netloc)
            raise
        return r.text.splitlines()

    @property
    def voices(self):
        r = self.session.get(self._makeurl('/voices'))
        r.raise_for_status()
        return [line.split()[0] for line in r.text.splitlines()]

    def _makeurl(self, path, query={}):
        query_s = urllib.urlencode(query)
        urlparts = ('http', self.netloc, path, query_s, '')
        return urlparse.urlunsplit(urlparts)

    def say(self, phrase):
        if self.language not in self.languages:
            raise ValueError("Language '%s' not supported" % self.language)

        if self.voice not in self.voices:
            raise ValueError("Voice '%s' not supported" % self.voice)
        query = {'OUTPUT_TYPE': 'AUDIO',
                 'AUDIO': 'WAVE_FILE',
                 'INPUT_TYPE': 'TEXT',
                 'INPUT_TEXT': phrase,
                 'LOCALE': self.language,
                 'VOICE': self.voice}

        r = self.session.get(self._makeurl('/process', query=query))
        return r.content
