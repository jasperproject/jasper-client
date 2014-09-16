# -*- coding: utf-8-*-
"""
    Iterates over all the WORDS variables in the modules and creates a dictionary for the client.
"""

import os
import g2p
from brain import Brain


def text2lm(in_filename, out_filename):
    """Wrapper around the language model compilation tools"""
    def text2idngram(in_filename, out_filename):
        cmd = "text2idngram -vocab %s < %s -idngram temp.idngram" % (out_filename,
                                                                     in_filename)
        os.system(cmd)

    def idngram2lm(in_filename, out_filename):
        cmd = "idngram2lm -idngram temp.idngram -vocab %s -arpa %s" % (
            in_filename, out_filename)
        os.system(cmd)

    text2idngram(in_filename, in_filename)
    idngram2lm(in_filename, out_filename)


def compile(sentences, dictionary, languagemodel):
    """
        Gets the words and creates the dictionary
    """

    modules = Brain.get_modules()

    words = []
    for module in modules:
        words.extend(module.WORDS)

    # for spotify module
    words.extend(["MUSIC", "SPOTIFY"])
    words = list(set(words))

    # create the dictionary
    pronounced = g2p.translateWords(words)
    zipped = zip(words, pronounced)
    lines = ["%s %s" % (x, y) for x, y in zipped]

    with open(dictionary, "w") as f:
        f.write("\n".join(lines) + "\n")

    # create the language model
    with open(sentences, "w") as f:
        f.write("\n".join(words) + "\n")
        f.write("<s> \n </s> \n")
        f.close()

    # make language model
    text2lm(sentences, languagemodel)
