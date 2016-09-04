import threading
import subprocess
import re
import os
import time
import tempfile
import Queue as queue

class VoiceIn(threading.Thread):
    def __init__(self, adcdev, lm, dict):
        super(VoiceIn, self).__init__()
        self._params = (adcdev, lm, dict)
        self._listening = False
        self.phrase_queue = queue.Queue()

    def listen(self, y):
        self._listening = y

    def run(self):
        # Thanks to the question and answers:
        # http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
        def execute(cmd):
            popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
            stdout_lines = iter(popen.stdout.readline, "")
            for stdout_line in stdout_lines:
                yield stdout_line

            popen.stdout.close()
            return_code = popen.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, cmd)

        cmd = 'pocketsphinx_continuous -adcdev %s -lm %s -dict %s -inmic yes' % self._params
        pattern = re.compile('^[0-9]{9}: (.+)')  # lines starting with 9 digits

        for out in execute(cmd.split(' ')):
            # Print out the line to give the same experience as
            # running pocketsphinx_continuous.
            print out,  # newline included by the line itself
            if self._listening:
                m = pattern.match(out)
                if m:
                    phrase = m.group(1).strip()
                    if phrase:
                        self.phrase_queue.put(phrase)

class VoiceOut(object):
    def __init__(self, device, resources):
        self._device = device

        if isinstance(resources, dict):
            self._resources = resources
        else:
            self._resources = {'beep_hi': os.path.join(resources, 'beep_hi.wav'),
                               'beep_lo': os.path.join(resources, 'beep_lo.wav')}

    def play(self, path):
        cmd = ['aplay', '-D', self._device, path]
        subprocess.call(cmd)

    def beep(self, high):
        f = self._resources['beep_hi' if high else 'beep_lo']
        self.play(f)

    def say(self, phrase):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name

        cmd = ['pico2wave', '--wave', fname, phrase.lower()]
                                          # Ensure lowercase because consecutive uppercases
                                          # sometimes cause it to spell out the letters.
        subprocess.call(cmd)

        self.play(fname)
        os.remove(fname)

def listen(vin, vout, callback,
           callsign='Judy', attention_span=10, forever=True):
    vin.daemon = True
    vin.start()

    def loop():
        while 1:
            vin.listen(True)
            ph = vin.phrase_queue.get(block=True)

            # Does the phrase end with my name?
            if ph.split(' ')[-1] == callsign.upper():
                vout.beep(1)  # high beep

                try:
                    ph = vin.phrase_queue.get(block=True, timeout=attention_span)
                except queue.Empty:
                    vout.beep(0)  # low beep
                else:
                    vout.beep(0)  # low beep

                    # Ignore further speech. Flush existing phrases.
                    vin.listen(False)
                    while not vin.phrase_queue.empty():
                        vin.phrase_queue.get(block=False)

                    callback(ph)

    # Have to put loop() in a thread. If I call loop() from within main thread,
    # Ctrl-C cannot kill the process because it hangs at queue.get().
    t = threading.Thread(target=loop)
    t.daemon = True
    t.start()

    if forever:
        if type(forever) is str:
            print forever

        while 1:
            time.sleep(10)
