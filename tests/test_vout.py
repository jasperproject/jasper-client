import judy

vout = judy.VoiceOut(device='plughw:0,0',
                     resources='/home/pi/judy/resources/audio')

vout.beep(1)
vout.beep(0)
vout.say('How are you today?')
