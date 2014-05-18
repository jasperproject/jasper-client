import subprocess
import os

def play(wav_file):
    try:
        subprocess.check_output("aplay -D hw:1,0 %s" % wav_file)
    except Exception, e:
        os.system("aplay %s" % wav_file)


