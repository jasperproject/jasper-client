"""
    Iterates over all the WORDS variables in the modules and creates a dictionary for the client.
"""

import glob
import os.path
import importlib

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

def create_languagemodel(words, output_file):
    """
        Creates the languagemodel from words
    """
    text = " ".join(words)
    cmuclmtk.text2lm(text, output_file)

def compile_words(words, dictionary, languagemodel):
    dictionary_file = jasperpath.dictionary(dictionary)
    languagemodel_file = jasperpath.languagemodel(languagemodel)
    
    create_dict(words, dictionary_file)
    create_languagemodel(words, languagemodel_file)

def compile(dictionary, languagemodel):
    """
        Creates the dictionary and languagemodel
    """
    words = get_words()
    compile_words(words, dictionary, languagemodel)

