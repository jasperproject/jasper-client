# -*- coding: utf-8-*-
import os
import tempfile
import subprocess
import re

PHONE_MATCH = re.compile(r'<s> (.*) </s>')
PHONETISAURUS_PATH = os.environ['JASPER_HOME'] + "/phonetisaurus"


def parseLine(line):
    return PHONE_MATCH.search(line).group(1)


def parseOutput(output):
    return PHONE_MATCH.findall(output)


def translateWord(word):
    out = subprocess.check_output(['phonetisaurus-g2p', '--model=%s' %
                                  PHONETISAURUS_PATH + "/g014b2b.fst", '--input=%s' % word])
    return parseLine(out)


def translateWords(words):
    full_text = '\n'.join(words)

    with tempfile.NamedTemporaryFile(suffix='.g2p', delete=False) as f:
        temp_filename = f.name
        f.write(full_text)

    output = translateFile(temp_filename)
    os.remove(temp_filename)

    return output


def translateFile(input_filename, output_filename=None):
    out = subprocess.check_output(['phonetisaurus-g2p', '--model=%s' %
        PHONETISAURUS_PATH + "/g014b2b.fst", '--input=%s' % input_filename, '--words', '--isfile'])
    out = parseOutput(out)

    if output_filename:
        out = '\n'.join(out)

        with open(output_filename, "wb") as f:
            f.write(out)

        return None

    return out

if __name__ == "__main__":

    translateFile(PHONETISAURUS_PATH + "/phonetisaurus/sentences.txt",
                  PHONETISAURUS_PATH + "/phonetisaurus/dictionary.dic")
