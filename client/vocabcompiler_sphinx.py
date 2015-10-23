# -*- coding: utf-8-*-
import os
import logging
import tempfile
from g2p import PhonetisaurusG2P
try:
    import cmuclmtk
except ImportError:
    logging.getLogger(__name__).error("Error importing CMUCLMTK module. " +
                                      "PocketsphinxVocabulary will not work " +
                                      "correctly.", exc_info=True)


def get_languagemodel_path(path):
    """
    Returns:
        The path of the the pocketsphinx languagemodel file as string
    """
    return os.path.join(path, 'languagemodel')


def get_dictionary_path(path):
    """
    Returns:
        The path of the pocketsphinx dictionary file as string
    """
    return os.path.join(path, 'dictionary')


def compile_vocabulary(directory, phrases, config):
    """
    Compiles the vocabulary to the Pocketsphinx format by creating a
    languagemodel and a dictionary.

    Arguments:
        phrases -- a list of phrases that this vocabulary will contain
    """
    logger = logging.getLogger(__name__)
    languagemodel_path = get_languagemodel_path(directory)
    dictionary_path = get_dictionary_path(directory)
    g2pconverter = PhonetisaurusG2P(config)

    logger.debug('Languagemodel path: %s' % languagemodel_path)
    logger.debug('Dictionary path:    %s' % dictionary_path)
    text = " ".join([("<s> %s </s>" % phrase) for phrase in phrases])
    logger.debug('Compiling languagemodel...')
    vocabulary = compile_languagemodel(text, languagemodel_path)
    logger.debug('Starting dictionary...')
    compile_dictionary(g2pconverter, vocabulary, dictionary_path)


def compile_languagemodel(text, output_file):
    """
    Compiles the languagemodel from a text.

    Arguments:
        text -- the text the languagemodel will be generated from
        output_file -- the path of the file this languagemodel will
                       be written to

    Returns:
        A list of all unique words this vocabulary contains.
    """
    logger = logging.getLogger(__name__)
    with tempfile.NamedTemporaryFile(suffix='.vocab', delete=False) as f:
        vocab_file = f.name

    # Create vocab file from text
    logger.debug("Creating vocab file: '%s'", vocab_file)
    cmuclmtk.text2vocab(text, vocab_file)

    # Create language model from text
    logger.debug("Creating languagemodel file: '%s'", output_file)
    cmuclmtk.text2lm(text, output_file, vocab_file=vocab_file)

    # Get words from vocab file
    logger.debug("Getting words from vocab file and removing it " +
                 "afterwards...")
    words = []
    with open(vocab_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('#') and line not in ('<s>', '</s>'):
                words.append(line)
    os.remove(vocab_file)

    return words


def compile_dictionary(g2pconverter, words, output_file):
    """
    Compiles the dictionary from a list of words.

    Arguments:
        words -- a list of all unique words this vocabulary contains
        output_file -- the path of the file this dictionary will
                       be written to
    """
    # create the dictionary
    logger = logging.getLogger(__name__)
    logger.debug("Getting phonemes for %d words...", len(words))
    phonemes = g2pconverter.translate(words)

    logger.debug("Creating dict file: '%s'", output_file)
    with open(output_file, "w") as f:
        for word, pronounciations in phonemes.items():
            for i, pronounciation in enumerate(pronounciations, start=1):
                if i == 1:
                    line = "%s\t%s\n" % (word, pronounciation)
                else:
                    line = "%s(%d)\t%s\n" % (word, i, pronounciation)
                f.write(line)
