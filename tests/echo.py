import judy

vin = judy.VoiceIn(adcdev='plughw:1,0',
                   lm='/home/pi/judy/resources/lm/0931.lm',
                   dict='/home/pi/judy/resources/lm/0931.dic')

vout = judy.VoiceOut(device='plughw:0,0',
                     resources='/home/pi/judy/resources/audio')

def handle(phrase):
    print 'Heard:', phrase
    vout.say(phrase)

judy.listen(vin, vout, handle)
