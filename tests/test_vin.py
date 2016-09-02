import judy

class VoiceOut(object):
    def play(self, path):
        print 'VoiceOut:Play:', path

    def beep(self, high):
        print 'VoiceOut:Beep:', 'HIGH' if high else 'LOW'

    def say(self, phrase):
        print 'VoiceOut:Say:', phrase

vin = judy.VoiceIn(adcdev='plughw:1,0',
                   lm='/home/pi/judy/resources/lm/0931.lm',
                   dict='/home/pi/judy/resources/lm/0931.dic')

vout = VoiceOut()

def handle(phrase):
    print 'Roger:', phrase

judy.listen(vin, vout, handle)
