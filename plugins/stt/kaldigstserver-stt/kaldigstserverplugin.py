import logging
import wave
import requests
from jasper import plugin


class KaldiGstServerSTTPlugin(plugin.STTPlugin):
    def __init__(self, *args, **kwargs):
        plugin.STTPlugin.__init__(self, *args, **kwargs)

        self._logger = logging.getLogger(__name__)
        self._http = requests.Session()

        self._url = self.config.get('url')

    def transcribe(self, fp):
        wav = wave.open(fp, 'rb')
        frame_rate = wav.getframerate()
        wav.close()
        data = fp.read()

        headers = {'Content-Type': 'audio/x-raw-int; rate=%s' % frame_rate}
        r = self._http.post(self._url, data=data, headers=headers)
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self._logger.critical('Request failed with http status %d',
                                  r.status_code)
            return []

        response = r.json()
        if not response['status'] == 0:
            if 'message' in response:
                msg = response['message']
            elif response['status'] == 1:
                msg = 'No speech found'
            elif response['status'] == 2:
                msg = 'Recognition aborted'
            elif response['status'] == 9:
                msg = 'All recognizer processes currently in use'
            else:
                msg = 'Unknown error'
            self._logger.critical('Transcription failed: %s', msg)
            return []

        results = []
        for hyp in response['hypotheses']:
            results.append(hyp['utterance'])

        self._logger.info('Transcribed: %r', results)
        return results
