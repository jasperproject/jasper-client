# -*- coding: utf-8-*-
"""
A drop-in replacement for the Mic class that allows for input I/O to
happen via provided audio file and output via string return. This is
intended to drive automated testing.

Unlike test_mic.py this does include both active and passive listening
in order to support testing and evaluation of wake words and related
configuration.
"""

import logging
import pyaudio


class Mic:
    prev = None

    def __init__(self, speaker, passive_stt_engine, active_stt_engine):
        """
        Initiates the pocketsphinx instance.

        Arguments:
        speaker -- handles platform-independent audio output
        passive_stt_engine -- performs STT while Jasper is in passive listen
                              mode
        acive_stt_engine -- performs STT while Jasper is in active listen mode
        """
        self._logger = logging.getLogger(__name__)
        self.speaker = speaker
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._audio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio completed.")

    def listen(self, stt_engine):
        with open(self.audio_input, 'rb') as f:
            return stt_engine.transcribe(f)

    def passiveListen(self, PERSONA):
        # check if PERSONA was said
        transcribed = self.listen(self.passive_stt_engine)

        if any(PERSONA in phrase for phrase in transcribed):
            return (False, PERSONA)

        return (False, transcribed)

    def activeListenToAllOptions(self, THRESHOLD=None, LISTEN=True,
                                 MUSIC=False):
        return [self.activeListen(THRESHOLD=THRESHOLD, LISTEN=LISTEN,
                                  MUSIC=MUSIC)]

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        if not LISTEN:
            return self.prev

        input = self.listen(self.active_stt_engine)
        self.prev = input
        return input

    def say(self, phrase, OPTIONS=None):
        self.text_output = phrase
