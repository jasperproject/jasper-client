"""
    Iterates over all the WORDS variables in the modules and creates a dictionary for the client.
"""

import os
import sys
import glob
import tempfile
import g2p
import jasperpath


def text2lm(in_filename, out_filename, in_filename2=None):
    """Wrapper around the language model compilation tools"""
    def text2idngram(in_filename, in_filename2, tmp_filename):
        cmd = 'text2idngram -idngram "%s" -vocab "%s" < "%s" ' % (tmp_filename, in_filename, in_filename2)
        os.system(cmd)
    def idngram2lm(in_filename, out_filename, tmp_filename):
        cmd = 'idngram2lm -idngram "%s" -vocab "%s" -arpa "%s"' % (tmp_filename, in_filename, out_filename)
        os.system(cmd)
    
    out_filename = jasperpath.vocab(out_filename)
    in_filename = jasperpath.vocab(in_filename)
    in_filename2 = jasperpath.vocab(in_filename2) if in_filename2 is not None else in_filename

    with tempfile.NamedTemporaryFile(suffix='.idngram',delete=False) as f:
        tmp_filename = f.name

    text2idngram(in_filename, in_filename2, tmp_filename)
    idngram2lm(in_filename, out_filename, tmp_filename)

    os.remove(tmp_filename)


def compile(sentences, dictionary, languagemodel):
    """
        Gets the words and creates the dictionary
    """
    module_files = glob.glob(jasperpath.clientmodules('*.py'))

    m = [os.path.basename(f)[:-3] for f in module_files]

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

    dictionary = jasperpath.vocab(dictionary)
    sentences = jasperpath.vocab(sentences)
    languagemodel = jasperpath.vocab(languagemodel)

    with open(dictionary, "w") as f:
        f.write("\n".join(lines) + "\n")

    # create the language model
    with open(sentences, "w") as f:
        f.write("\n".join(words) + "\n")
        f.write("<s> \n </s> \n")

    # make language model
    text2lm(sentences, languagemodel)
