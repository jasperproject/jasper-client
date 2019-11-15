# -*- coding: utf-8-*-
import logging
from notifier import Notifier
from brain import Brain

from subprocess import Popen, PIPE

def bounce():
    scpt = '''
        tell application "Logic Pro X" to activate
        delay 1
        tell application "System Events"
          keystroke "b" using command down
          delay 1
          keystroke return
        end tell
        '''
    args = []

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    print (p.returncode, stdout, stderr)

def record():
    scpt = '''
        tell application "Logic Pro X" to activate
        delay 1
        tell application "System Events"
          keystroke "r"
        end tell
        '''
    args = []

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    print (p.returncode, stdout, stderr)

def stop_req():
    scpt = '''
        tell application "Logic Pro X" to activate
        delay 1
        tell application "System Events"
          key code 49
        end tell
        '''
    args = []

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    print (p.returncode, stdout, stderr)

def copy_track():
    scpt = '''
        tell application "Logic Pro X" to activate
        delay 1
        tell application "System Events"
          keystroke "d" using command down
        end tell
        '''
    args = []

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    print (p.returncode, stdout, stderr)

def bring_begin():
    scpt = '''
        tell application "System Events"
          keystroke return
        end tell
        '''
    args = []

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    print (p.returncode, stdout, stderr)

def confirm():
    scpt = '''
        tell application "System Events"
          keystroke return
        end tell
        '''
    args = []

    p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(scpt)
    print (p.returncode, stdout, stderr)


class Conversation(object):

    def __init__(self, persona, mic, profile):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = mic
        self.profile = profile
        self.brain = Brain(mic, profile)
        self.notifier = Notifier(profile)

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation with keyword '%s'.",
                          self.persona)
        while True:
            # Print notifications until empty
            notifications = self.notifier.getAllNotifications()
            for notif in notifications:
                self._logger.info("Received notification: '%s'", str(notif))

            self._logger.debug("Started listening for keyword '%s'",
                               self.persona)
            threshold, transcribed = self.mic.passiveListen(self.persona)
            found = (transcribed + [''])[0]
            if 'AMOS' not in found: continue

            if 'BOUNCE' in found or 'BALANCE' in found:
                print("BOUNCEING...")
                bounce()
            if 'REC' in found or 'RECORD' in found or 'START' in found:
                print("RECORDING...")
                record()
            if 'STOP' in found or 'END' in found:
                print("STOPPING...")
                stop_req()
            if 'DUPLICATE' in found or 'COPY' in found:
                print("COPYING...")
                copy_track()
            if 'FRONT' in found or 'BEGINING' in found or 'FRONT' in found:
                print("BRINGING BEGIN...")
                bring_begin()
            if 'CONFIRM' in found or 'YES' in found or 'ENTER' in found or 'CONTINUE' in found:
                print("CONFIRMING...")
                confirm()

            self._logger.debug("Stopped listening for keyword '%s'",
                               self.persona)

            if not transcribed or not threshold:
                self._logger.info("Nothing has been said or transcribed.")
                continue
            self._logger.info("Keyword '%s' has been said!", self.persona)

            self._logger.debug("Started to listen actively with threshold: %r",
                               threshold)
            input = self.mic.activeListenToAllOptions(threshold)
            self._logger.debug("Stopped to listen actively with threshold: %r",
                               threshold)

            if input:
                self.brain.query(input)
            else:
                self.mic.say("Pardon?")
