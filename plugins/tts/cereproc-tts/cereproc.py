import os
import tempfile
import suds
import urllib
from client import plugin

VOICES = [
    ('Adam', 'en-US'),
    ('Caitlin', 'en-IE'),
    ('Claire', 'en-GB'),
    ('Dodo', 'en-GB'),
    ('Giles', 'en-GB'),
    ('Hannah', 'en-US'),
    ('Heather', 'en-GB'),
    ('Isabella', 'en-US'),
    ('Jack', 'en-GB'),
    ('Jess', 'en-GB'),
    ('Katherine', 'en-US'),
    ('Kirsty', 'en-GB'),
    ('Lauren', 'en-GB'),
    ('Nathan', 'en-US'),
    ('Nicole', 'en-FR'),
    ('Sarah', 'en-GB'),
    ('Stuart', 'en-GB'),
    ('Sue', 'en-GB'),
    ('William', 'en-GB'),
    ('Nuria', 'ca-ES'),
    ('Anne', 'nl-NL'),
    ('Laurent', 'fr-FR'),
    ('Suzanne', 'fr-FR'),
    ('Alex', 'de-DE'),
    ('Gudrun', 'de-DE'),
    ('Leopold', 'de-AT'),
    ('Laura', 'it-IT'),
    ('Yuki', 'jp-JP'),
    ('Gabriel', 'pt-BR'),
    ('Lucia', 'pt-PT'),
    ('Sara', 'es-ES')
]


class CereprocTTSPlugin(plugin.TTSPlugin):
    """
    Uses the CereVoice Cloud Text-to-Speech Web Service.
    The CereVoice Cloud is a text-to-speech (TTS) software-as-a-service (SAAS)
    from CereProc.
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        try:
            self._account_id = self.profile['cereproc-tts']['account_id']
        except KeyError:
            raise ValueError("Cereproc account ID not configured!")

        try:
            self._password = self.profile['cereproc-tts']['password']
        except KeyError:
            raise ValueError("Cereproc password not configured!")

        try:
            language = self.profile['language']
        except KeyError:
            language = 'en-US'

        try:
            voice = self.profile['cereproc-tts']['voice']
        except KeyError:
            voice = None

        if voice is None:
            for name, lang in VOICES:
                if language == lang:
                    voice = name
                    break
        else:
            if not any(voice == name for name, language in VOICES):
                voice = None

        if voice is None:
            raise ValueError('Invalid voice!')

        self._voice = voice

        self._soapclient = suds.client.Client(
            "https://cerevoice.com/soap/soap_1_1.php?WSDL")

    def say(self, phrase):
        reply = self._soapclient.service.speakExtended(
            self._account_id, self._password, self._voice,
            phrase.decode('utf-8'), "wav", 22050, False, False)

        if reply.resultCode != 1:
            return False
        else:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                tmpfile = f.name
            urllib.urlretrieve(reply.fileUrl, tmpfile)
            with open(tmpfile, 'r') as f:
                data = f.read()
            os.remove(tmpfile)

        return data
