import requests
import mstranslator
from jasper import plugin


class MicrosoftTranslatorTTSPlugin(plugin.TTSPlugin):
    """
    Uses the Microsoft Translator API.
    See http://www.microsoft.com/en-us/translator/getstarted.aspx.
    """

    def __init__(self, *args, **kwargs):
        plugin.TTSPlugin.__init__(self, *args, **kwargs)

        try:
            client_id = self.profile['mstranslator-tts']['client_id']
        except KeyError:
            raise ValueError('Microsoft Translator client ID not configured!')

        try:
            client_secret = self.profile['mstranslator-tts'][
                'client_secret']
        except KeyError:
            raise ValueError(
                'Microsoft Translator client secret not configured!')

        try:
            language = self.profile['language']
        except KeyError:
            language = 'en-US'

        self._mstranslator = mstranslator.Translator(client_id, client_secret)

        available_languages = self._mstranslator.get_langs(speakable=True)
        for lang in (language.lower(), language.lower().split('-')[0]):
            if lang in available_languages:
                self._language = lang
                break
        else:
            raise ValueError("Language '%s' not supported" % language)

        try:
            best_quality = self.profile['mstranslator-tts'][
                'best_quality']
        except KeyError:
            best_quality = False

        self._kwargs = {
            'format': 'audio/wav',
            'best_quality': best_quality
        }

    def say(self, phrase):
        """ Method used to utter words using the MS Translator TTS plugin """
        url = self._mstranslator.speak(phrase, self._language, **self._kwargs)
        r = requests.get(url)
        return r.content
