# -*- coding: utf-8-*-
import os
import re
import subprocess
import tempfile
import logging

import yaml

import diagnose
import jasperpath


class PhonetisaurusG2P(object):
    PATTERN = re.compile(r'^(?P<word>.+)\t(?P<precision>\d+\.\d+)\t<s> ' +
                         r'(?P<pronounciation>.*) </s>', re.MULTILINE)

    @classmethod
    def execute(cls, fst_model, input, is_file=False, nbest=None):
        logger = logging.getLogger(__name__)

        cmd = ['phonetisaurus-g2p',
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
            for word, precision, pronounc in cls.PATTERN.findall(stdoutdata):
                if word not in result:
                    result[word] = []
                result[word].append(pronounc)
        return result

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as pull request
        # jasperproject/jasper-client#128 has been merged

        conf = {'fst_model': os.path.join(jasperpath.APP_PATH, os.pardir,
                                          'phonetisaurus', 'g014b2b.fst')}
        # Try to get fst_model from config
        profile_path = jasperpath.config('profile.yml')
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                profile = yaml.safe_load(f)
                if 'pocketsphinx' in profile:
                    if 'fst_model' in profile['pocketsphinx']:
                        conf['fst_model'] = \
                            profile['pocketsphinx']['fst_model']
                    if 'nbest' in profile['pocketsphinx']:
                        conf['nbest'] = int(profile['pocketsphinx']['nbest'])
        return conf

    def __new__(cls, fst_model=None, *args, **kwargs):
        if not diagnose.check_executable('phonetisaurus-g2p'):
            raise OSError("Can't find command 'phonetisaurus-g2p'! Please " +
                          "check if Phonetisaurus is installed and in your " +
                          "$PATH.")
        if fst_model is None or not os.access(fst_model, os.R_OK):
            raise OSError(("FST model '%r' does not exist! Can't create " +
                           "instance.") % fst_model)
        inst = object.__new__(cls, fst_model, *args, **kwargs)
        return inst

    def __init__(self, fst_model=None, nbest=None):
        self._logger = logging.getLogger(__name__)

        self.fst_model = os.path.abspath(fst_model)
        self._logger.debug("Using FST model: '%s'", self.fst_model)

        self.nbest = nbest
        if self.nbest is not None:
            self._logger.debug("Will use the %d best results.", self.nbest)

    def _translate_word(self, word):
        return self.execute(self.fst_model, word, nbest=self.nbest)

    def _translate_words(self, words):
        with tempfile.NamedTemporaryFile(suffix='.g2p', delete=False) as f:
            # The 'delete=False' kwarg is kind of a hack, but Phonetisaurus
            # won't work if we remove it, because it seems that I can't open
            # a file descriptor a second time.
            for word in words:
                f.write("%s\n" % word)
            tmp_fname = f.name
        output = self.execute(self.fst_model, tmp_fname, is_file=True,
                              nbest=self.nbest)
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

if __name__ == "__main__":
    import pprint
    import argparse
    parser = argparse.ArgumentParser(description='Phonetisaurus G2P module')
    parser.add_argument('fst_model', action='store',
                        help='Path to the FST Model')
    parser.add_argument('--debug', action='store_true',
                        help='Show debug messages')
    args = parser.parse_args()

    logging.basicConfig()
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)

    words = ['THIS', 'IS', 'A', 'TEST']

    g2pconv = PhonetisaurusG2P(args.fst_model, nbest=3)
    output = g2pconv.translate(words)

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(output)
