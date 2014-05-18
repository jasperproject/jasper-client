import wave
import pyaudio
import time

def play(wav_file):
    wf = wave.open(wav_file, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(1024)

    while data != '':
        stream.write(data)
        data = wf.readframes(1024)

    time.sleep(.5)
    stream.stop_stream()
    stream.close()
    p.terminate()