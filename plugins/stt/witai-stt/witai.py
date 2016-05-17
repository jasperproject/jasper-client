import logging
import requests
from jasper import plugin

# There seems to be no way to get language setting of the defined app
# Last updated: April 06, 2016
SUPPORTED_LANG = (
    'de',
    'en',
    'es',
    'et',
    'fr',
    'it',
    'nl',
    'pl',
    'pt',
    'ru',
    'sv'
)


class WitAiSTTPlugin(plugin.STTPlugin):
    """
    Speech-To-Text implementation which relies on the Wit.ai Speech API.

    This implementation requires an Wit.ai Access Token to be present in
    profile.yml. Please sign up at https://wit.ai and copy your instance
    token, which can be found under Settings in the Wit console to your
    profile.yml:
        ...
        stt_engine: witai-stt
        witai-stt:
          access_token:    ERJKGE86SOMERANDOMTOKEN23471AB
    """

    def __init__(self, *args, **kwargs):
        """
        Create Plugin Instance
        """
        plugin.STTPlugin.__init__(self, *args, **kwargs)
        self._logger = logging.getLogger(__name__)
        self.token = self.profile['witai-stt']['access_token']

        try:
            language = self.profile['language']
        except KeyError:
            language = 'en-US'
        if language.split('-')[0] not in SUPPORTED_LANG:
            raise ValueError('Language %s is not supported.',
                             language.split('-')[0])

    @property
    def token(self):
        """
        Return defined acess token.
        """
        return self._token

    @property
    def language(self):
        """
        Returns selected language
        """
        return self._language

    @token.setter
    def token(self, value):
        """
        Sets property token
        """
        self._token = value
        self._headers = {'Authorization': 'Bearer %s' % self.token,
                         'accept': 'application/json',
                         'Content-Type': 'audio/wav'}

    @property
    def headers(self):
        """
        Return headers
        """
        return self._headers

    def transcribe(self, fp):
        """
        transcribes given audio file by uploading to wit.ai and returning
        received text from json answer.
        """
        data = fp.read()
        r = requests.post('https://api.wit.ai/speech?v=20150101',
                          data=data,
                          headers=self.headers)
        try:
            r.raise_for_status()
            text = r.json()['_text']
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with response: %r',
                                  r.text,
                                  exc_info=True)
            return []
        except requests.exceptions.RequestException:
            self._logger.critical('Request failed.', exc_info=True)
            return []
        except ValueError as e:
            self._logger.critical('Cannot parse response: %s',
                                  e.args[0])
            return []
        except KeyError:
            self._logger.critical('Cannot parse response.',
                                  exc_info=True)
            return []
        else:
            transcribed = [text.upper()]
            self._logger.info('Transcribed: %r', transcribed)
            return transcribed
