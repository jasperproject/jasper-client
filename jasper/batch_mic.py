# -*- coding: utf-8 -*-
"""
A drop-in replacement for the Mic class that allows for batch mode operation.
Useful for debugging. Unlike with the typical Mic implementation, Jasper
processes the given commands in the batchfile.
"""
import os.path
import logging


def parse_batch_file(fp):
    # parse given batch file and get the filenames or commands
    for line in fp:
        line = line.partition('#')[0].rstrip()
        if line:
            yield line


class Mic(object):
    def __init__(self, passive_stt_engine, active_stt_engine,
                 batch_file, keyword='JASPER'):
        self._logger = logging.getLogger(__name__)
        self._keyword = keyword
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self._commands = parse_batch_file(batch_file)

    def transcribe_command(self, command):
        # check if command is a filename
        if os.path.isfile(command):
            # handle it as mic input
            try:
                fp = open(command, 'r')
            except (OSError, IOError) as e:
                self._logger.error('Failed to open "%s": %s',
                                   command, e.strerror)
            else:
                transcribed = self.active_stt_engine.transcribe(fp)
                fp.close()
        else:
            # handle it as text input
            transcribed = [command]
        return transcribed

    def wait_for_keyword(self, keyword="JASPER"):
        return

    def active_listen(self, timeout=3):
        try:
            command = next(self._commands)
        except StopIteration:
            raise SystemExit
        else:
            transcribed = self.transcribe_command(command)
            if transcribed:
                print('YOU: %r' % transcribed)
            return transcribed

    def listen(self):
        return self.active_listen()

    def say(self, phrase, OPTIONS=None):
        print("JASPER: %s" % phrase)
