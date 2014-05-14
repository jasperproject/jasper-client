# This Python file uses the following encoding: utf-8
"""
    The Mic class handles all interactions with the microphone and speaker.
"""

import os
import json
from wave import open as open_audio
import audioop
import pyaudio
import alteration
import urllib2
import urllib
import json
import goslate
import yaml

# quirky bug where first import doesn't work
try:
    import pocketsphinx as ps
except:
    import pocketsphinx as ps

langCode = None

profile = yaml.safe_load(open("profile.yml", "r"))

class Mic:

    speechRec = None
    speechRec_persona = None
    langCode = None

    def __init__(self, lmd, dictd, lmd_persona, dictd_persona, lmd_music=None, dictd_music=None):
        """
            Initiates the pocketsphinx instance.

            Arguments:
            lmd -- filename of the full language model
            dictd -- filename of the full dictionary (.dic)
            lmd_persona -- filename of the 'Persona' language model (containing, e.g., 'Jasper')
            dictd_persona -- filename of the 'Persona' dictionary (.dic)
        """
        hmdir = "/usr/local/share/pocketsphinx/model/hmm/en_US/hub4wsj_sc_8k"

        if lmd_music and dictd_music:
            self.speechRec_music = ps.Decoder(hmm = hmdir, lm = lmd_music, dict = dictd_music)
        self.speechRec_persona = ps.Decoder(
            hmm=hmdir, lm=lmd_persona, dict=dictd_persona)
        self.speechRec = ps.Decoder(hmm=hmdir, lm=lmd, dict=dictd)

    def transcribe(self, audio_file_path, profile=profile, PERSONA_ONLY=False, MUSIC=False, GOOGLE=True):
        """
            Performs TTS, transcribing an audio file and returning the result.

            Arguments:
            audio_file_path -- the path to the audio file to-be transcribed
            PERSONA_ONLY -- if True, uses the 'Persona' language model and dictionary
            MUSIC -- if True, uses the 'Music' language model and dictionary
        """

        wavFile = file(audio_file_path, 'rb')
        wavFile.seek(44)
        
        RATE = 16000
	global langCode
	langCode = None

        if MUSIC:
            self.speechRec_music.decode_raw(wavFile)
            result = self.speechRec_music.get_hyp()
        elif PERSONA_ONLY:
            self.speechRec_persona.decode_raw(wavFile)
            result = self.speechRec_persona.get_hyp()
        elif GOOGLE:
            result1 = self.googleTranslate()
	    profile_langCode = profile["langCode"]
	    if profile_langCode != "en-US":
	        result2 = self.googleTranslate(langCode=profile_langCode)
	        if result1[1] > result2[1]:
		    result = str(result1[0])
		    resultLangCode = str(result1[2])
	        elif result1[1] < result2[1]:
		    result = str(result2[0])
		    resultLangCode = str(result2[2])
	        else:
		    result = "no_info"
		    resultLangCode = "en-US"
	    else:
		result = str(result1[0])
		resultLangCode = "en-US"
            # Debug file
	    text_file = open("result.txt","w")
            text_file.write(str(result1[0]) + " | " + str(result1[1]) + " | " + str(result1[2]) + "\n")
	    if profile_langCode != "en-US":
                text_file.write(str(result2[0]) + " | " + str(result2[1]) + " | " + str(result2[2]))
            text_file.close()

            return [ str(result) , resultLangCode ]
	else:
            self.speechRec.decode_raw(wavFile)
            result = self.speechRec.get_hyp()
        
        print "==================="
        print "JASPER: " + result[0]
        print "==================="

	return [ result[0] , "en-US" ]

    def getScore(self, data):
        rms = audioop.rms(data, 2)
        score = rms / 3
        return score

    def fetchThreshold(self):

        # TODO: Consolidate all of these variables from the next three
        # functions
        THRESHOLD_MULTIPLIER = 1.8
        AUDIO_FILE = "passive.wav"
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

	stream.stop_stream()
	stream.close()
	audio.terminate()

        return THRESHOLD

    def passiveListen(self, PERSONA):
        """
            Listens for PERSONA in everyday sound
            Times out after LISTEN_TIME, so needs to be restarted
        """

        THRESHOLD_MULTIPLIER = 1.8
        AUDIO_FILE = "passive.wav"
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
	    stream.stop_stream()
            stream.close()
            audio.terminate()
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
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(1)
        write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        write_frames.setframerate(RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()

        # check if PERSONA was said
        transcribed = self.transcribe(AUDIO_FILE, PERSONA_ONLY=True)[0]

        if PERSONA in transcribed:
            return (THRESHOLD, PERSONA)

        return (False, transcribed)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False, GOOGLE=False):
        """
            Records until a second of silence or times out after 12 seconds
        """

        AUDIO_FILE = "active.wav"
        RATE = 16000
        CHUNK = 1024
        LISTEN_TIME = 20

        # user can request pre-recorded sound
        if not LISTEN:
            if not os.path.exists(AUDIO_FILE):
                return None

            return self.transcribe(AUDIO_FILE)[0]

        # check if no threshold provided
        if THRESHOLD == None:
            THRESHOLD = self.fetchThreshold()

        os.system("aplay beep_hi.wav")

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
        lastN = [THRESHOLD * 1.2 for i in range(40)]

        for i in range(0, RATE / CHUNK * LISTEN_TIME):

            data = stream.read(CHUNK)
            frames.append(data)
            score = self.getScore(data)

            lastN.pop(0)
            lastN.append(score)

            average = sum(lastN) / float(len(lastN))

	    # force Jasper to wait a moment for you to start talking
	    #     before deciding that you've stopped.
	    if i > RATE / CHUNK * float(LISTEN_TIME / 4):
                # TODO: 0.8 should not be a MAGIC NUMBER!
                if average < THRESHOLD * 0.8:
                    break

        os.system("aplay beep_lo.wav")

        # save the audio data
        stream.stop_stream()
        stream.close()
        audio.terminate()
        write_frames = open_audio(AUDIO_FILE, 'wb')
        write_frames.setnchannels(1)
        write_frames.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        write_frames.setframerate(RATE)
        write_frames.writeframes(''.join(frames))
        write_frames.close()

        # DO SOME AMPLIFICATION
        # os.system("sox "+AUDIO_FILE+" temp.wav vol 20dB")
	#os.system("avconv -i "+AUDIO_FILE+" -filter 'volume=volume=+20db:precision=float' temp.wav")

        if MUSIC:
            return self.transcribe(AUDIO_FILE, MUSIC=True)[0]
            
        if GOOGLE:
            return self.transcribe(AUDIO_FILE, GOOGLE=True)

        return self.transcribe(AUDIO_FILE)[0]
        
    def say(self, phrase, translate=False, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav"):
	if type(phrase) is list:
	    phrase = phrase[0]

	if translate:
	    if langCode != None and langCode != "en-US":
		self.langCode = "en-US"
	    else:
		self.langCode = profile["langCode"]
	else:
	    self.langCode = langCode

        if self.langCode != None and self.langCode != "en-US":
            gs = goslate.Goslate()
	    phrase = gs.translate( phrase, self.langCode)
	    content = phrase.split(" ")
	    result = ""
	    count = 0
	    length = len(content)
	    try:
		for word in content:
	            count += 1
            	    if len(result) < 90:
                        result = result + " " + word
        	    else:
                        self.googleSpeak(str(self.langCode), result)
                        result = word
        	    if count == length:
                        self.googleSpeak(str(self.langCode), result)
		return
	    except:
		pass
		#self.googleSpeak("en-US", result="Uh Oh... we have a problem.")
	    return
        # alter phrase before speaking
        phrase = alteration.clean(phrase)

        os.system("espeak " + json.dumps(phrase) + OPTIONS )
        os.system("aplay say.wav")

    def googleSpeak(self, langCode, phrase):
            url = "http://translate.google.com/translate_tts?tl=%s&q=%s" % (langCode, urllib.quote_plus(phrase))
            text_file = open("url.txt","w")
            text_file.write(str(url))
            text_file.close()
            hrs = {"User-Agent":
                   "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7"}
            request = urllib2.Request( url , headers = hrs)
            page = urllib2.urlopen(request)
            file = open("say.mp3", 'wb')
            file.write(page.read())
            file.close()
#            os.system("ffplay -nodisp -autoexit say.mp3")
	    os.system("avconv -y -i say.mp3 say.wav")
            os.system("aplay say.wav")
            return

    def googleTranslate(self, langCode='en-US'):
	    """
		This Function Translates Speech to text from
		 english or polish into english for JASPER

		It can be adapted for any language supported by google
		 by changing profile.yaml to any language code from
		 the list found at:
		 https://developers.google.com/translate/v2/using_rest#language-params
	    """
	    gs = goslate.Goslate()

	    RATE = 16000
            os.system("avconv -y -i active.wav -ar 16000 -acodec flac active.flac")
            flac = open("active.flac", 'rb')
            data = flac.read()
            flac.close()
            url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=%s" % langCode
	    try:
                req = urllib2.Request(
		    url,
                    data=data,
                    headers={
                        'Content-type': 'audio/x-flac; rate=%s' % RATE})
            
                response_url = urllib2.urlopen(req)
                response_read = response_url.read()
                response_read = response_read.decode('utf-8')
            except urllib2.URLError:
                return [ "no_info" , 0 , str(langCode) ]
            if response_read:
		jsdata = None
                try:
		    allData = response_read.splitlines()
		    for line in allData:
			# This is specific to the json returned by google.
			# Debug File
#                    	text_file = open("json.txt","w")
                    	#text_file.write(line)

#			jsdata = json.loads( response_read )

#			text_file.close()

			try:
			    if jsdata == None:
				jsdata = json.loads(line)
			    if jsdata["status"] == 5:
				jsdata = None
			except:
			    pass

                    if not jsdata:
                        return [ "no_info" , 0 , str(langCode) ]

		    text_file = open("json.txt","w")
		    text_file.write(str(jsdata))
		    text_file.close()

		    result = jsdata["hypotheses"][0]["utterance"]
                    confidence = jsdata["hypotheses"][0]["confidence"]
                    if langCode != "en-US":
                       	result = gs.translate(result, 'en_US').decode('utf-8')
#		    if langCode == "en-US" and result != result2:
#			result = resultEnglish
#		    elif langCode != "en-US":
#			result = resultEnglish

                    print "==================="
                    print "JASPER: " + result
                    print "==================="

		    return [ str(result), float(confidence), str(langCode) ]
                except IndexError:
		    return [ "no_info" , 0 , str(langCode) ]
            else:
                return [ "no_info" , 0 , str(langCode) ]
