# -*- coding: utf-8 -*-
"""
A drop-in replacement for the Mic class that allows for batch mode operation. Useful for debugging. Unlike with the typical Mic
implementation, Jasper processes the given commands in the batchfile.
"""
import os.path
import logging
import sys

class Mic(object):      

    def __init__(self, passive_stt_engine, active_stt_engine,
                 batchfilecontent, keyword='JASPER'):
	#mic.Mic.__init__(self, input_device, output_device,
        #         passive_stt_engine, active_stt_engine,
        #         tts_engine, config, keyword='JASPER')
        self._logger = logging.getLogger(__name__)
        self._keyword = keyword        
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine        
	self._batchcommands=batchfilecontent
	self._nbrcommands=len(batchfilecontent)
	self._batched_cmds=0
        return

    def transcribe_batchcommand(self, stt_engine):

	#still unprocessed commands?
	if self._nbrcommands<=self._batched_cmds: return False

	command = self._batchcommands[self._batched_cmds]
	self._batched_cmds += 1
	#check if command is a filename	
	if os.path.isfile(command):
		#let's try open it  
		fileid = None 		
		try:
        		fileid = open(command, "r")
    		except IOError:
        		self._logger.error("The file %s does not exist!" % command)   
		else:
			#handle it as mic input
			try:
                    		transcribed = stt_engine.transcribe(fileid)				
                	except:
                    		dbg = (self._logger.getEffectiveLevel() == logging.DEBUG)
                    		self._logger.error("Transcription failed!", exc_info=dbg)
				transcribed = False
	else:
		#handle it as text input	
		transcribed = [command]


	return transcribed

    def wait_for_keyword(self, keyword="JASPER"):
        return

    def active_listen(self, timeout=3):
	#get transcribtion - either using audio or text
	transcribed = self.transcribe_batchcommand(self.active_stt_engine)
	if transcribed:			
		print "YOU: " + " ".join(transcribed)
        return transcribed

    def listen(self):
	#still unprocessed commands?
	if self._nbrcommands<=self._batched_cmds:
		 self._logger.info("processed %i commands. Done.", self._batched_cmds)
		 sys.exit(0)
	
	#get transcribtion - either using audio or text
	transcribed = self.transcribe_batchcommand(self.passive_stt_engine)
	if transcribed:		
		print "YOU: " + " ".join(transcribed)

	#check for keyword	
	if transcribed and any([self._keyword.lower() in t.lower() for t in transcribed if t]):
		self._logger.info("Keyword %s has been uttered", self._keyword)
		return self.active_listen(timeout=3)	
	else: return False

    def say(self, phrase, OPTIONS=None):
        print("JASPER: %s" % phrase)
