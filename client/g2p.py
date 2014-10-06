# -*- coding: utf-8-*-
import os
import tempfile
import subprocess
import re
import yaml

import jasperpath

PHONE_MATCH = re.compile(r'<s> (.*) </s>')

FST_MODEL = None

# Try to get fst_model from config
profile_path = os.path.join(os.path.dirname(__file__), 'profile.yml')
if os.path.exists(profile_path):
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f)
        if ('pocketsphinx' in profile and
           'fst_model' in profile['pocketsphinx']):
            FST_MODEL = profile['pocketsphinx']['fst_model']

if not FST_MODEL:
    FST_MODEL = os.path.join(jasperpath.APP_PATH, os.pardir, 'phonetisaurus',
                             'g014b2b.fst')


def parseLine(line):
    return PHONE_MATCH.search(line).group(1)


def parseOutput(output):
    return PHONE_MATCH.findall(output)


def translateWord(word):
    out = subprocess.check_output(
        ['phonetisaurus-g2p', '--model=%s' % FST_MODEL, '--input=%s' % word])
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
    out = subprocess.check_output(
        ['phonetisaurus-g2p', '--model=%s' % FST_MODEL,
         '--input=%s' % input_filename, '--words', '--isfile'])
    out = parseOutput(out)

    if output_filename:
        out = '\n'.join(out)

        with open(output_filename, "wb") as f:
            f.write(out)

        return None

    return out
