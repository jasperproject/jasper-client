"""
    Iterates over all the WORDS variables in the modules and creates a dictionary for the client.
"""

import glob
import os.path
import importlib
import tempfile

import jasperpath
import g2p
import cmuclmtk
import brain

def get_words(additional_words=['MUSIC','SPOTIFY']):
    """
        Gets the words from modules
    """
    words = []

    # For spotify module
    words.extend(additional_words)

    modules = brain.get_modules()
    for mod in modules:
        words.extend(mod.WORDS)

    return words

def create_dict(words, output_file):
    """
        Creates the dictionary from words
    """
    # create the dictionary
    pronounced = g2p.translateWords(words)
    zipped = zip(words, pronounced)
    lines = ["%s %s" % (x, y) for x, y in zipped]

    with open(output_file, "w") as f:
        for line in lines:
            f.write("%s\n" % line)

def create_languagemodel(text, output_file):
    """
        Creates the languagemodel from text, returns a list of words in vocabulary
    """
    with tempfile.NamedTemporaryFile(suffix='.vocab', delete=False) as f:
        vocab_file = f.name

    # Create vocab file from text
    cmuclmtk.text2vocab_file(text, vocab_file)
    # Create language model from text
    cmuclmtk.text2lm(text, output_file, vocab_file=vocab_file)
    words = []
    with open(vocab_file,'r',) as f:
        for line in f:
            line = line.strip()
            if not line.startswith('#') and not line in ('<s>','</s>'):
                words.append(line)
    os.remove(vocab_file)
    # return used vocabulary
    return words


def compile_text(text, name="default"):

    dictionary_file = jasperpath.dictionary(name)
    languagemodel_file = jasperpath.languagemodel(name)
    
    if not '<s>' in text:
        text = "<s> %s </s>" % compile_text
    words = create_languagemodel(text, languagemodel_file)
    create_dict(words, dictionary_file)
    return words

def compile(name="default"):
    """
        Creates the dictionary and languagemodel
    """
    words = get_words()
    text = " ".join(["<s> %s </s>" % word for word in words])
    compile_text(text, name=name)