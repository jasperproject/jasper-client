import os
import subprocess
import re
import tempfile
import jasperpath

PHONE_MATCH = re.compile(r'<s> (.*) </s>')

PHONETISAURUS_MODEL = jasperpath.phonetisaurus('scripts', 'g014b2b', 'g014b2b.fst')

def parseLine(line):
    return PHONE_MATCH.search(line).group(1)


def parseOutput(output):
    return PHONE_MATCH.findall(output)


def translateWord(word):
    out = subprocess.check_output(['phonetisaurus-g2p', '--model=%s' %  PHONETISAURUS_MODEL, '--input=%s' % word])
    return parseLine(out)


def translateWords(words):
    full_text = '\n'.join(words)

    with tempfile.NamedTemporaryFile(suffix=".g2p", delete=False) as f:
        f.write(full_text)
        TEMP_FILENAME = f.name

    output = translateFile(TEMP_FILENAME)
    os.remove(TEMP_FILENAME)

    return output


def translateFile(input_filename, output_filename=None):
    out = subprocess.check_output(['phonetisaurus-g2p', '--model=%s' % PHONETISAURUS_MODEL, '--input=%s' % input_filename, '--words', '--isfile'])
    out = parseOutput(out)

    if output_filename:
        out = '\n'.join(out)

        with open(output_filename, "wb") as f:
            f.write(out)

        return None

    return out

if __name__ == "__main__":
    sentences_path = jasperpath.config('sentences.txt')
    dictionary_path = jasperpath.config('dictionary.dic')
    translateFile(sentences_path,dictionary_path)
