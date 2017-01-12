# -*- coding: utf-8 -*-
import unittest
from jasper import paths
from jasper import testutils
from .. import sphinxplugin


class TestPocketsphinxSTTPlugin(unittest.TestCase):

    def setUp(self):
        self.jasper_clip = paths.data('audio', 'jasper.wav')
        self.time_clip = paths.data('audio', 'time.wav')

        try:
            self.passive_stt_engine = testutils.get_genericplugin_instance(
                sphinxplugin.PocketsphinxSTTPlugin)
            self.passive_stt_engine.init('unittest-passive', ['JASPER'])
            self.active_stt_engine = testutils.get_genericplugin_instance(
                sphinxplugin.PocketSphinxSTTPlugin)
            self.active_stt_engine.init('unittest-active', ['TIME'])
        except ImportError:
            self.skipTest("Pockersphinx not installed!")

    def testTranscribeJasper(self):
        """
        Does Jasper recognize his name (i.e., passive listen)?
        """
        with open(self.jasper_clip, mode="rb") as f:
            transcription = self.passive_stt_engine.transcribe(f)
        self.assertIn("JASPER", transcription)

    def testTranscribe(self):
        """
        Does Jasper recognize 'time' (i.e., active listen)?
        """
        with open(self.time_clip, mode="rb") as f:
            transcription = self.active_stt_engine.transcribe(f)
        self.assertIn("TIME", transcription)
