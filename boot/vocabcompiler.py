"""
    This iterates over all the WORDS variables in the modules and creates a dictionary that the client program will use
"""

import os
import sys
import pkgutil

lib_path = os.path.abspath('../client')
sys.path.append(lib_path)
import modules
import g2p


def compile():
    """
        Gets the words and creates the dictionary
    """

    m = dir(modules)

    words = []
    for module_name in m:
        try:
            eval("words.extend(modules.%s.WORDS)" % module_name)
        except:
            pass  # module probably doesn't have the property

    words = list(set(words))

    # for spotify module
    words.extend(["MUSIC","SPOTIFY"])

    # create the dictionary
    pronounced = g2p.translateWords(words)
    zipped = zip(words, pronounced)
    lines = ["%s %s" % (x, y) for x, y in zipped]

    with open("../client/dictionary.dic", "w") as f:
        f.write("\n".join(lines) + "\n")

    # create the language model
    with open("../client/sentences.txt", "w") as f:
        f.write("\n".join(words) + "\n")
        f.write("<s> \n </s> \n")
        f.close()

    # make language model
    os.system(
        "text2idngram -vocab ../client/sentences.txt < ../client/sentences.txt -idngram temp.idngram")
    os.system(
        "idngram2lm -idngram temp.idngram -vocab ../client/sentences.txt -arpa ../client/languagemodel.lm")
