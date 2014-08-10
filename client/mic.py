"""
    The Mic class handles all interactions with the microphone and speaker.
"""

import os
import json
import tempfile
from contextlib import contextmanager

from wave import open as open_audio
import audioop
import pyaudio
import alteration

import jasperpath


class Mic:

    speechRec = None
    speechRec_persona = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine):
        """
            Initiates the pocketsphinx instance.

            Arguments:
            speaker -- handles platform-independent audio output
            passive_stt_engine -- performs STT while Jasper is in passive listen mode
            acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        self.speaker = speaker
	self.ar = AudioRecorder(16000, pyaudio.paInt16, 1, 1024)
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine


    def passiveListen(self, PERSONA, timeout=10, delay_multiplier=1):
        """
            Listens for 'PERSONA' in everyday sound
            Times out after 'timeout' (in seconds), so needs to be restarted
        """

        threshold = self.ar.get_threshold()

        # save some memory for sound data
        frames = []

        # flag raised when sound disturbance detected
        didDetect = False

        with self.ar.record_audio_stream() as stream:
            # start passively listening for disturbance above threshold
            for i in range(0, self.ar.rate_chunk_ratio * timeout):

                data = stream.read(self.ar.chunksize)
                frames.append(data)
                score = self.ar.get_score(data)

                if score > threshold:
                    didDetect = True
                    # cutoff any recording before this disturbance was detected
                    frames = frames[-20:]
                    # let's keep recording for few seconds and save the file
                    for i in range(0, self.ar.rate_chunk_ratio * delay_multiplier):
                        data = stream.read(self.ar.chunksize)
                        frames.append(data)

        # no use continuing if no flag raised
        if not didDetect:
            raise NoDisturbanceDetectedException()
            return (None, None)

        # save the audio data
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            self.ar.save_audio(f, frames)
            audio_file_path = f.name

        # check if PERSONA was said
        transcribed = self.passive_stt_engine.transcribe(audio_file_path, PERSONA_ONLY=True)

        if PERSONA in transcribed:
            return (threshold, PERSONA)

        return (None, transcribed)

    def activeListen(self, threshold=None, timeout=12, audio_file=None, music=False):
        """
            Records until a second of silence or times out after 12 seconds
        """

        # user can request pre-recorded sound
        if audio_file:
            if not os.path.exists(audio_file):
                return None
            transcribe_file = audio_file
        else:
            # check if no threshold provided
            if not threshold:
                threshold = self.ar.get_threshold()

            self.speaker.play(jasperpath.data("audio", "beep_hi.wav"))

            frames = []

            # increasing the range # results in longer pause after command
            # generation
            lastN = [threshold * 1.2 for i in range(30)]

            for data in self.ar.record_audio_data(seconds):
                frames.append(data)
                score = self.ar.get_score(data)

                lastN.pop(0)
                lastN.append(score)

                average = sum(lastN) / float(len(lastN))

                # TODO: 0.8 should not be a MAGIC NUMBER!
                if average <  threshold * 0.8:
                    break

            self.speaker.play(jasperpath.data("audio", "beep_lo.wav"))

            # Save recorded data as .wav file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                self.ar.save_audio(f, frames)
                transcribe_file = tmpfile_path = f.name

        # Transcribe the .wav file
        transcribed = self.active_stt_engine.transcribe(transcribe_file, music)
        
        if not audio_file:
            # Remove the temporary .wav file afterwards
            os.remove(tmpfile_path)

        return transcribed

    def say(self, phrase):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)

class NoDisturbanceDetectedException(Exception):
    pass

class AudioRecorder(object):
    def __init__(self, rate, format, channels, chunksize):
        self.rate = rate
        self.format = format
        self.channels = channels
        self.chunksize = chunksize

    @property
    def rate_chunk_ratio(self):
        return (self.rate / self.chunksize)

    @contextmanager
    def record_audio_stream(self):
        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunksize)

        yield stream
        # close recording stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

    def record_audio_data(self, seconds):
        with self.record_audio_stream() as stream:
            for i in range(0, self.rate_chunk_ratio * seconds):
                yield stream.read(self.chunksize)

    @classmethod
    def get_score(cls, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def get_threshold(self, multiplier=1.8, seconds=1):
        # TODO: Consolidate parameter default values

        # stores the lastN score values
        lastN = [i for i in range(20)]

        # calculate the long run average, and thereby the proper threshold
        for data in self.record_audio_data(seconds):
            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.get_score(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        threshold = average * multiplier

        return threshold

    def save_audio(self, fp, frames):
        sample_width = pyaudio.get_sample_size(self.format)
        f = open_audio(fp, 'wb')
        f.setsampwidth(sample_width)
        f.setframerate(self.rate)
        f.setnchannels(1)
        f.writeframes(''.join(frames))
        f.close()
