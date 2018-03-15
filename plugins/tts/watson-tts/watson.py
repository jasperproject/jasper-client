import json
import tempfile
import logging
import requests
from jasper import plugin


class IBMWatsonTTSPlugin(plugin.TTSPlugin):
    """
        Text-To-Speech implementation which relies on the IBM Watson Text To Speech API.

        This implementation requires an IBM Cloud Text-To-Speech API key to be present in profile.yml

        To obtain an API key:
        1. Sign up for a free IBM Cloud Account:
           https://console.bluemix.net/registration/
        2. Create a Text-To-Speech Instance through the IBM Cloud console:
           https://console.bluemix.net/catalog/services/text-to-speech
        3. Select your Text-To-Speech Instance and Click Service Credentials.
        4. Click New Credential. Name Credential "Jasper Credential" or appropriate.
        5. Add your credential username/password to your profile.yml. Add a 'watson_stt' entry
           section and set your 'username' and 'password'.
        6. Set the value of the 'tts_engine' key in your profile.yml to 'watson'

        Excerpt from sample profile.yml:

            ...
            timezone: US/Pacific
            tts_engine: watson
            watson_tts:
                username: $YOUR_API_USERNAME
                password: $YOUR_API_PASSWORD

    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)
        # FIXME: get init args from config

        self._logger = logging.getLogger(__name__)
        self._endpoint_url = 'https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize'
        self._username = None
        self._password = None
        self._voice = 'en-US_MichaelVoice'
        self._http = requests.Session()

        self.username = self.profile['watson_tts']['username']
        self.password = self.profile['watson_tts']['password']

    @property
    def endpoint_url(self):
        return self._endpoint_url

    @property
    def voice(self):
        return self._voice

    @voice.setter
    def voice(self, value):
        self._voice = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value

    def say(self, phrase):
        """
            Performs TTS via the IBM Watson Text-To-Speech API, synthesizing voice audio
            and returning an audio file.

            Arguments:
            phrase -- the text to synthesize into audio
        """

        if not self.username:
            self._logger.critical('API username missing, synthesize request aborted.')
            return []
        elif not self.password:
            self._logger.critical('API password missing, synthesize request aborted.')
            return []

        auth = (self.username, self.password)
        params = {'voice': self.voice}
        payload = {'text': phrase}
        headers = {'content-type': 'application/json', 'accept': 'audio/wav;rate=48000'}
        r = self._http.post(
            self.endpoint_url,
            data=json.dumps(payload),
            params=params,
            headers=headers,
            auth=auth
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with http status %d: %s', r.status_code, r.text)
            if r.status_code == requests.codes['forbidden']:
                self._logger.warning('Status 403 is probably caused by ' +
                                     'invalid IBM Cloud API credentials.')

        data = None
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
            f.seek(0)
            data = f.read()

        return data
