import os

def play(wav_file):
    if os.system("aplay -D hw:1,0 %s" % wav_file) != 0:
        os.system("aplay %s" % wav_file)


