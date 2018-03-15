import logging
import wave
import requests
from jasper import plugin


class IBMWatsonSTTPlugin(plugin.STTPlugin):
    """
    Speech-To-Text implementation which relies on the IBM Watson Speech To Text API.

    This implementation requires an IBM Cloud Speech-To-Text API key to be present in profile.yml

    To obtain an API key:
    1. Sign up for a free IBM Cloud Account:
       https://console.bluemix.net/registration/
    2. Create a Speech-To-Text Instance through the IBM Cloud console:
       https://console.bluemix.net/catalog/services/speech-to-text
    3. Select your Speech-To-Text Instance and Click Service Credentials.
    4. Click New Credential. Name Credential "Jasper Credential" or appropriate.
    5. Add your credential username/password to your profile.yml. Add a 'watson_stt' entry
       section and set your 'username' and 'password'.
    6. Set the value of the 'stt_engine' key in your profile.yml to 'watson'

    Excerpt from sample profile.yml:

        ...
        timezone: US/Pacific
        stt_engine: watson
        watson_stt:
            username: $YOUR_API_USERNAME
            password: $YOUR_API_PASSWORD
            model: en-US_BroadbandModel

    """

    def __init__(self, *args, **kwargs):
        plugin.STTPlugin.__init__(self, *args, **kwargs)
        # FIXME: get init args from config

        self._logger = logging.getLogger(__name__)
        self._endpoint_url = 'https://stream.watsonplatform.net/speech-to-text/api/v1/recognize'
        self._username = None
        self._password = None
        self._model = 'en-US_BroadbandModel'
        self._http = requests.Session()

        self.username = self.profile['watson_stt']['username']
        self.password = self.profile['watson_stt']['password']

    @property
    def endpoint_url(self):
        return self._endpoint_url

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value

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

    def transcribe(self, fp):
        """
        Performs STT via the IBM Watson Speech-To-Text API, transcribing an audio
        file and returning an English string.

        Arguments:
        audio_file_path -- the path to the .wav file to be transcribed
        """

        if not self.username:
            self._logger.critical('API username missing, transcription request aborted.')
            return []
        elif not self.password:
            self._logger.critical('API password missing, transcription request aborted.')
            return []

        wav = wave.open(fp, 'rb')
        frame_rate = wav.getframerate()
        wav.close()
        data = fp.read()

        auth = (self.username, self.password)
        params = {'inactivity_timeout': 30}
        headers = {'Content-Type': 'audio/l16; rate=%s' % frame_rate}
        r = self._http.post(
            self.endpoint_url,
            data=data,
            params=params,
            headers=headers,
            auth=auth
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with http status %d', r.status_code)
            if r.status_code == requests.codes['forbidden']:
                self._logger.warning('Status 403 is probably caused by ' +
                                     'invalid IBM Cloud API credentials.')
            return []
        r.encoding = 'utf-8'
        try:
            response = r.json()
            if len(response['results']) == 0:
                # Response result is empty
                raise ValueError('Nothing has been transcribed.')
            results = [result['alternatives'][0]['transcript'] for result in response['results']]
        except ValueError as e:
            self._logger.warning('Empty response: %s', e.args[0])
            results = []
        except (KeyError, IndexError):
            self._logger.warning('Cannot parse response.', exc_info=True)
            results = []
        else:
            # Convert all results to uppercase
            results = tuple(result.upper() for result in results)
            self._logger.info('Transcribed: %r', results)
        return results
