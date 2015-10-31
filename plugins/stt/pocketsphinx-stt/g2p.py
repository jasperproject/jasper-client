# -*- coding: utf-8 -*-
import os
import re
import subprocess
import tempfile
import logging


RE_WORDS = re.compile(r'^(?P<word>.+)\t(?P<precision>\d+\.\d+)\t<s> ' +
                      r'(?P<pronounciation>.*) </s>', re.MULTILINE)


def execute(executable, fst_model, input, is_file=False, nbest=None):
    logger = logging.getLogger(__name__)

    cmd = [executable,
           '--model=%s' % fst_model,
           '--input=%s' % input,
           '--words']

    if is_file:
        cmd.append('--isfile')

    if nbest is not None:
        cmd.extend(['--nbest=%d' % nbest])

    cmd = [str(x) for x in cmd]
    try:
        # FIXME: We can't just use subprocess.call and redirect stdout
        # and stderr, because it looks like Phonetisaurus can't open
        # an already opened file descriptor a second time. This is why
        # we have to use this somehow hacky subprocess.Popen approach.
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdoutdata, stderrdata = proc.communicate()
    except OSError:
        logger.error("Error occured while executing command '%s'",
                     ' '.join(cmd), exc_info=True)
        raise

    if stderrdata:
        for line in stderrdata.splitlines():
            message = line.strip()
            if message:
                logger.debug(message)

    if proc.returncode != 0:
        logger.error("Command '%s' return with exit status %d",
                     ' '.join(cmd), proc.returncode)
        raise OSError("Command execution failed")

    result = {}
    if stdoutdata is not None:
        for word, precision, pronounc in RE_WORDS.findall(stdoutdata):
            if word not in result:
                result[word] = []
            result[word].append(pronounc)
    return result


class PhonetisaurusG2P(object):
    def __init__(self, executable, fst_model, nbest=None):
        self._logger = logging.getLogger(__name__)

        self.executable = executable

        self.fst_model = os.path.abspath(fst_model)
        self._logger.debug("Using FST model: '%s'", self.fst_model)

        self.nbest = nbest
        if self.nbest is not None:
            self._logger.debug("Will use the %d best results.", self.nbest)

    def _translate_word(self, word):
        return execute(self.executable, self.fst_model, word,
                       nbest=self.nbest)

    def _translate_words(self, words):
        with tempfile.NamedTemporaryFile(suffix='.g2p', delete=False) as f:
            # The 'delete=False' kwarg is kind of a hack, but Phonetisaurus
            # won't work if we remove it, because it seems that I can't open
            # a file descriptor a second time.
            for word in words:
                f.write("%s\n" % word)
            tmp_fname = f.name
        output = execute(self.executable, self.fst_model, tmp_fname,
                         is_file=True, nbest=self.nbest)
        os.remove(tmp_fname)
        return output

    def translate(self, words):
        if type(words) is str or len(words) == 1:
            self._logger.debug('Converting single word to phonemes')
            output = self._translate_word(words if type(words) is str
                                          else words[0])
        else:
            self._logger.debug('Converting %d words to phonemes', len(words))
            output = self._translate_words(words)
        self._logger.debug('G2P conversion returned phonemes for %d words',
                           len(output))
        return output
