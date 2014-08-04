"""
    The Mic class handles all interactions with the microphone and speaker.
"""

import os
import json
import tempfile
from wave import open as open_audio
import audioop
import pyaudio
import alteration

import jasperpath

# quirky bug where first import doesn't work
try:
    import pocketsphinx as ps
except:
    import pocketsphinx as ps


class Mic:

    speechRec = None
    speechRec_persona = None

    def __init__(self, speaker, lmd, dictd, lmd_persona, dictd_persona, lmd_music=None, dictd_music=None):
        """
            Initiates the pocketsphinx instance.

            Arguments:
            speaker -- handles platform-independent audio output
            lmd -- filename of the full language model
            dictd -- filename of the full dictionary (.dic)
            lmd_persona -- filename of the 'Persona' language model (containing, e.g., 'Jasper')
            dictd_persona -- filename of the 'Persona' dictionary (.dic)
        """
        self.speaker = speaker

        if lmd_music and dictd_music:
            self.speechRec_music = ps.Decoder(hmm=jasperpath.HMM_PATH, lm=lmd_music, dict=dictd_music)
        self.speechRec_persona = ps.Decoder(
            hmm=jasperpath.HMM_PATH, lm=lmd_persona, dict=dictd_persona)
        self.speechRec = ps.Decoder(hmm=jasperpath.HMM_PATH, lm=lmd, dict=dictd)

    def transcribe(self, audio_file_path, PERSONA_ONLY=False, MUSIC=False):
        """
            Performs TTS, transcribing an audio file and returning the result.

            Arguments:
            audio_file_path -- the path to the audio file to-be transcribed
            PERSONA_ONLY -- if True, uses the 'Persona' language model and dictionary
            MUSIC -- if True, uses the 'Music' language model and dictionary
        """
        wavFile = open(audio_file_path,"rb")
        wavFile.seek(44)

        if MUSIC:
            self.speechRec_music.decode_raw(wavFile)
            result = self.speechRec_music.get_hyp()
        elif PERSONA_ONLY:
            self.speechRec_persona.decode_raw(wavFile)
            result = self.speechRec_persona.get_hyp()
        else:
            self.speechRec.decode_raw(wavFile)
            result = self.speechRec.get_hyp()

        print "==================="
        print "JASPER: " + result[0]
        print "==================="

        return result[0]

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self):

        # TODO: Consolidate all of these variables from the next three
        # functions
        THRESHOLD_MULTIPLIER = 1.8
        RATE = 16000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10

        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(20)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        return THRESHOLD

    def passiveListen(self, PERSONA):
        """
            Listens for PERSONA in everyday sound
            Times out after LISTEN_TIME, so needs to be restarted
        """

        THRESHOLD_MULTIPLIER = 1.8
        RATE = 16000
        CHUNK = 1024

        # number of seconds to allow to establish threshold
        THRESHOLD_TIME = 1

        # number of seconds to listen before forcing restart
        LISTEN_TIME = 10

        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)
        # stores the audio data
        frames = []

        # stores the lastN score values
        lastN = [i for i in range(30)]

        # calculate the long run average, and thereby the proper threshold
        for i in range(0, RATE / CHUNK * THRESHOLD_TIME):

            data = stream.read(CHUNK)
            frames.append(data)

            # save this data point as a score
            lastN.pop(0)
            lastN.append(self.getScore(data))
            average = sum(lastN) / len(lastN)

        # this will be the benchmark to cause a disturbance over!
        THRESHOLD = average * THRESHOLD_MULTIPLIER

        # save some memory for sound data
        frames = []

        # flag raised when sound disturbance detected
        didDetect = False

        # start passively listening for disturbance above threshold
        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)

            if score > THRESHOLD:
                didDetect = True
                break

        # no use continuing if no flag raised
        if not didDetect:
            print "No disturbance detected"
            return

        # cutoff any recording before this disturbance was detected
        frames = frames[-20:]
        # otherwise, let's keep recording for few seconds and save the file
        DELAY_MULTIPLIER = 1
        for i in range(0, RATE / CHUNK * DELAY_MULTIPLIER):

            data = stream.read(CHUNK)
            frames.append(data)
        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
            write_frames = open_audio(audio_file, 'wb')
            write_frames.setnchannels(1)
            write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            write_frames.setframerate(RATE)
            write_frames.writeframes(''.join(frames))
            write_frames.close()
            audio_file_path = audio_file.name
        # check if PERSONA was said
        transcribed = self.transcribe(audio_file_path, PERSONA_ONLY=True)
        os.remove(audio_file_path)

        if PERSONA in transcribed:
            return (THRESHOLD, PERSONA)

        return (False, transcribed)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        """
            Records until a second of silence or times out after 12 seconds
        """

        RATE = 16000
        CHUNK = 1024
        LISTEN_TIME = 12

        # user can request pre-recorded sound
        if not LISTEN:
            if not os.path.exists(AUDIO_FILE):
                return None

            return self.transcribe(AUDIO_FILE)

        # check if no threshold provided
        if THRESHOLD == None:
            THRESHOLD = self.fetchThreshold()

        self.speaker.play("../static/audio/beep_hi.wav")

        # prepare recording stream
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        frames = []
        # increasing the range # results in longer pause after command
        # generation
        lastN = [THRESHOLD * 1.2 for i in range(30)]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)

            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))

            # TODO: 0.8 should not be a MAGIC NUMBER!
            if average < THRESHOLD * 0.8:
                break

        self.speaker.play("../static/audio/beep_lo.wav")

        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as audio_file:
            write_frames = open_audio(audio_file, 'wb')
            write_frames.setnchannels(1)
            write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            write_frames.setframerate(RATE)
            write_frames.writeframes(''.join(frames))
            write_frames.close()
            audio_file_path = audio_file.name

        # DO SOME AMPLIFICATION 
        # os.system("sox "+audio_file_path+" temp.wav vol 20dB")

        transcribed = self.transcribe(audio_file_path, MUSIC=MUSIC)
        return transcribed

    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
        # alter phrase before speaking
        phrase = alteration.clean(phrase)
        self.speaker.say(phrase)
