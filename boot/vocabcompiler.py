"""
    Iterates over all the WORDS variables in the modules and creates a dictionary for the client.
"""

import os
import sys
import glob

lib_path = os.path.abspath('../client')
mod_path = os.path.abspath('../client/modules/')

sys.path.append(lib_path)
sys.path.append(mod_path)

import g2p


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

    m = [os.path.basename(f)[:-3]
         for f in glob.glob(os.path.dirname("../client/modules/") + "/*.py")]

    words = []
    for module_name in m:
        try:
            exec("import %s" % module_name)
            eval("words.extend(%s.WORDS)" % module_name)
        except:
            pass  # module probably doesn't have the property

    words = list(set(words))

    # for spotify module
    words.extend(["MUSIC", "SPOTIFY"])

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
