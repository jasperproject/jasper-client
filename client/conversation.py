# -*- coding: utf-8-*-
import logging
import signal
import os
from notifier import Notifier
from brain import Brain
from snowboy import snowboydecoder

class Conversation(object):

    def __init__(self, mic, profile):
        self._logger = logging.getLogger(__name__)
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        self.notifier = Notifier(profile)
        self.interrupted = False

    def signal_handler(self, signal, frame):
        self.interrupted = True

    def interrupt_callback(self):
        return self.interrupted

    def startListenningActively(self):
        threshold = None
        self._logger.debug("Started to listen actively with threshold: %r",
                               threshold)
        input = self.mic.activeListenToAllOptions(threshold)
        self._logger.debug("Stopped to listen actively with threshold: %r",
                               threshold)
        print("i'm here now")
        if input:
            self.brain.query(input)
        else:
            self.mic.say("Pardon?")

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation")

        TOP_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_FILE = os.path.join(TOP_DIR, "snowboy/model.pmdl")

        signal.signal(signal.SIGINT, self.signal_handler)
        detector = snowboydecoder.HotwordDetector(MODEL_FILE, sensitivity=0.5)
        print('Listening... Press Ctrl+C to exit')

        # main loop
        detector.start(detected_callback=self.startListenningActively,
               interrupt_check=self.interrupt_callback,
               sleep_time=0.03)

        detector.terminate()