import os
import subprocess
import re

TEMP_FILENAME = "g2ptemp"
PHONE_MATCH = re.compile(r'<s> (.*) </s>')


def parseLine(line):
    return PHONE_MATCH.search(line).group(1)


def parseOutput(output):
    return PHONE_MATCH.findall(output)


def translateWord(word):
    out = subprocess.check_output(['phonetisaurus-g2p', '--model=%s' %
                                  os.path.expanduser("~/phonetisaurus/g014b2b.fst"), '--input=%s' % word])
    return parseLine(out)


def translateWords(words):
    full_text = '\n'.join(words)

    f = open(TEMP_FILENAME, "wb")
    f.write(full_text)
    f.flush()

    output = translateFile(TEMP_FILENAME)
    os.remove(TEMP_FILENAME)

    return output


def translateFile(input_filename, output_filename=None):
    out = subprocess.check_output(['phonetisaurus-g2p', '--model=%s' % os.path.expanduser(
        "~/phonetisaurus/g014b2b.fst"), '--input=%s' % input_filename, '--words', '--isfile'])
    out = parseOutput(out)

    if output_filename:
        out = '\n'.join(out)

        f = open(output_filename, "wb")
        f.write(out)
        f.close()

        return None

    return out

if __name__ == "__main__":

    translateFile(os.path.expanduser("~/phonetisaurus/sentences.txt"),
                  os.path.expanduser("~/phonetisaurus/dictionary.dic"))
