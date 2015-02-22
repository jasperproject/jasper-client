# -*- coding: utf-8-*-
import logging
import tempfile
import wave
import audioop
import collections
import contextlib
import threading
import Queue as queue

import alteration

import jasperpath


class Mic(object):
    """
    The Mic class handles all interactions with the microphone and speaker.
    """

    def __init__(self, input_device, output_device,
                 passive_stt_engine, active_stt_engine,
                 tts_engine, keyword='JASPER'):
        self._logger = logging.getLogger(__name__)
        self._keyword = keyword
        self.tts_engine = tts_engine
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self._input_device = input_device
        self._output_device = output_device
        self._input_rate = 16000
        self._input_channels = 1
        self._input_bits = 16
        self._input_chunksize = 1024
        self._threshold = self._get_threshold()

    # Input methods
    def _get_threshold(self):
        self._logger.debug("Recording silence...")
        recording = self._input_device.record(self._input_chunksize,
                                              self._input_bits,
                                              self._input_channels,
                                              self._input_rate)
        rms = max([audioop.rms(recording.next(), self._input_bits / 8) for i in range(30)])
        self._logger.debug("Finished recording silence, Threshold is %r", rms)
        return rms

    @contextlib.contextmanager
    def _write_frames_to_file(self, frames):
        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(self._input_channels)
            wav_fp.setsampwidth(int(self._input_bits/8))
            wav_fp.setframerate(self._input_rate)
            wav_fp.writeframes(''.join(frames))
            wav_fp.close()
            f.seek(0)
            yield f

    def check_for_keyword(self, frame_queue, keyword_uttered, keyword):
        while True:
            frames = frame_queue.get()
            with self._write_frames_to_file(frames) as f:
                try:
                    transcribed = self.passive_stt_engine.transcribe(f)
                except:
                    pass
                else:
                    if transcribed and any([keyword.lower() in t.lower()
                                            for t in transcribed if t]):
                        keyword_uttered.set()
                finally:
                    frame_queue.task_done()

    def wait_for_keyword(self, keyword):
        frame_queue = queue.Queue()
        keyword_uttered = threading.Event()

        # FIXME: not configurable yet
        num_worker_threads = 2

        for i in range(num_worker_threads):
            t = threading.Thread(target=self.check_for_keyword,
                                 args=(frame_queue, keyword_uttered, keyword))
            t.daemon = True
            t.start()

        frames = collections.deque([], 10)
        recording = False
        recording_frames = []
        for frame in self._input_device.record(self._input_chunksize,
                                               self._input_bits,
                                               self._input_channels,
                                               self._input_rate):
            if keyword_uttered.is_set():
                self._logger.info("Keyword %s has been uttered", keyword)
                return
            frames.append(frame)
            if not recording:
                if self._threshold < audioop.rms(frame, self._input_bits / 8):
                    # Loudness is higher than normal, start recording and use
                    # the last 10 frames to start
                    self._logger.debug("Started recording on device '%s'",
                                       self._input_device.slug)
                    recording = True
                    recording_frames = []
                    recording_frames.extend(frames)
            else:
                # We're recording
                recording_frames.append(frame)
                if len(recording_frames) > (len(frames) + 10):
                    # If we recorded at least 20 frames, check if we're below
                    # threshold again
                    last_frames = recording_frames[-10:]
                    avg_rms = float(sum([audioop.rms(frame, self._input_bits / 8)
                                         for frame in last_frames]))/10
                    self._logger.debug("Recording's RMS/Threshold ratio: %f",
                                       (avg_rms/self._threshold))
                    if avg_rms < self._threshold:
                        # The loudness of the sound is not at least as high as
                        # the the threshold, we'll stop recording now
                        recording = False
                        self._logger.debug("Recorded %d frames",
                                           len(recording_frames))
                        frame_queue.put(tuple(recording_frames))

    def listen(self):
        self.wait_for_keyword(self._keyword)
        return self.active_listen()

    def active_listen(self, timeout=2):
        # record until <timeout> second of silence
        n = int(round((self._input_rate * (self._input_bits / 8) / self._input_chunksize)*timeout))
        self.play_file(jasperpath.data('audio', 'beep_hi.wav'))
        frames = []
        for frame in self._input_device.record(self._input_chunksize,
                                               self._input_bits,
                                               self._input_channels,
                                               self._input_rate):
            frames.append(frame)
            if len(frames) > n:
                avg_rms = float(sum([audioop.rms(frame, self._input_bits / 8)
                                     for frame in frames[-n:]]))/n
                if avg_rms < self._threshold:
                    break
        self.play_file(jasperpath.data('audio', 'beep_lo.wav'))
        with self._write_frames_to_file(frames) as f:
            return self.active_stt_engine.transcribe(f)

    # Output methods
    def play_file(self, filename):
        self._output_device.play_file(filename)

    def say(self, phrase):
        altered_phrase = alteration.clean(phrase)
        with tempfile.SpooledTemporaryFile() as f:
            f.write(self.tts_engine.say(altered_phrase))
            f.seek(0)
            self._output_device.play_fp(f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("stt").setLevel(logging.WARNING)
    audio = Mic.get_instance()
    while True:
        text = audio.listen()[0]
        if text:
            audio.say(text)
