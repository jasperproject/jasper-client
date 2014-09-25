# -*- coding: utf-8-*-
"""
Iterates over all the WORDS variables in the modules and creates a
vocabulary for the respective stt_engine if needed.
"""

import os
import tempfile
import logging
import hashlib
from abc import ABCMeta, abstractmethod, abstractproperty

import g2p
import brain
try:
    import cmuclmtk
except:
    logging.getLogger(__name__).error("Error importing CMUCLMTK module. " +
                                      "PocketsphinxVocabulary will not work " +
                                      "correctly.", exc_info=True)


class AbstractVocabulary(object):
    """
    Abstract base class for Vocabulary classes.

    Please note that subclasses have to implement the compile_vocabulary()
    method and set a string as the PATH_PREFIX class attribute.
    """
    __metaclass__ = ABCMeta

    @classmethod
    def phrases_to_revision(self, phrases):
        """
        Calculates a revision from phrases by using the SHA1 hash function.

        Arguments:
            phrases -- a list of phrases

        Returns:
            A revision string for given phrases.
        """
        sorted_phrases = sorted(phrases)
        joined_phrases = '\n'.join(sorted_phrases)
        sha1 = hashlib.sha1()
        sha1.update(joined_phrases)
        return sha1.hexdigest()

    def __init__(self, name='default', path='.'):
        """
        Initializes a new Vocabulary instance.

        Optional Arguments:
            name -- (optional) the name of the vocabulary (Default: 'default')
            path -- (optional) the path in which the vocabulary exists or will
                    be created (Default: '.')
        """
        self.name = name
        self.path = os.path.abspath(os.path.join(path, self.PATH_PREFIX, name))
        self._logger = logging.getLogger(__name__)

    @property
    def revision_file(self):
        """
        Returns:
            The path of the the revision file as string
        """
        return os.path.join(self.path, 'revision')

    @abstractproperty
    def is_compiled(self):
        """
        Checks if the vocabulary is compiled by checking if the revision file
        is readable. This method should be overridden by subclasses to check
        for class-specific additional files, too.

        Returns:
            True if the dictionary is compiled, else False
        """
        return os.access(self.revision_file, os.R_OK)

    @property
    def compiled_revision(self):
        """
        Reads the compiled revision from the revision file.

        Returns:
            the revision of this vocabulary (i.e. the string
            inside the revision file), or None if is_compiled
            if False
        """
        if not self.is_compiled:
            return None
        with open(self.revision_file, 'r') as f:
            revision = f.read().strip()
        self._logger.debug("compiled_revision is '%s'", revision)
        return revision

    def matches_phrases(self, phrases):
        """
        Convenience method to check if this vocabulary exactly contains the
        phrases passed to this method.

        Arguments:
            phrases -- a list of phrases

        Returns:
            True if phrases exactly matches the phrases inside this
            vocabulary.

        """
        return (self.compiled_revision == self.phrases_to_revision(phrases))

    def compile(self, phrases, force=False):
        """
        Compiles this vocabulary. If the force argument is True, compilation
        will be forced regardless of necessity (which means that the
        preliminary check if the current revision already equals the
        revision after compilation will be skipped).
        This method is not meant to be overridden by subclasses - use the
        _compile_vocabulary()-method instead.

        Arguments:
            phrases -- a list of phrases that this vocabulary will contain
            force -- (optional) forces compilation (Default: False)

        Returns:
            The revision of the compiled vocabulary
        """
        revision = self.phrases_to_revision(phrases)
        if not force and self.compiled_revision == revision:
            self._logger.debug('Compilation not neccessary, compiled ' +
                               'version matches phrases.')
            return revision

        if not os.path.exists(self.path):
            self._logger.debug("Vocabulary dir '%s' does not exist, " +
                               "creating...", self.path)
            try:
                os.makedirs(self.path)
            except OSError:
                self._logger.error("Couldn't create vocabulary dir '%s'",
                                   self.path, exc_info=True)
                raise
        try:
            with open(self.revision_file, 'w') as f:
                f.write(revision)
        except (OSError, IOError):
            self._logger.error("Couldn't write revision file in '%s'",
                               self.revision_file, exc_info=True)
            raise
        else:
            self._logger.info('Starting compilation...')
            try:
                self._compile_vocabulary(phrases)
            except Exception as e:
                self._logger.error("Fatal compilation Error occured, " +
                                   "cleaning up...", exc_info=True)
                try:
                    os.remove(self.revision_file)
                except OSError:
                    pass
                raise e
            else:
                self._logger.info('Compilation done.')
        return revision

    @abstractmethod
    def _compile_vocabulary(self, phrases):
        """
        Abstract method that should be overridden in subclasses with custom
        compilation code.

        Arguments:
            phrases -- a list of phrases that this vocabulary will contain
        """
        pass


class DummyVocabulary(AbstractVocabulary):

    PATH_PREFIX = 'dummy-vocabulary'

    @property
    def is_compiled(self):
        """
        Checks if the vocabulary is compiled by checking if the revision
        file is readable.

        Returns:
            True if this vocabulary has been compiled, else False
        """
        return super(self.__class__, self).is_compiled

    def _compile_vocabulary(self, phrases):
        """
        Does nothing (because this is a dummy class for testing purposes).
        """
        pass


class PocketsphinxVocabulary(AbstractVocabulary):

    PATH_PREFIX = 'pocketsphinx-vocabulary'

    @property
    def languagemodel_file(self):
        """
        Returns:
            The path of the the pocketsphinx languagemodel file as string
        """
        return os.path.join(self.path, 'languagemodel')

    @property
    def dictionary_file(self):
        """
        Returns:
            The path of the pocketsphinx dictionary file as string
        """
        return os.path.join(self.path, 'dictionary')

    @property
    def is_compiled(self):
        """
        Checks if the vocabulary is compiled by checking if the revision,
        languagemodel and dictionary files are readable.

        Returns:
            True if this vocabulary has been compiled, else False
        """
        return (super(self.__class__, self).is_compiled and
                os.access(self.languagemodel_file, os.R_OK) and
                os.access(self.dictionary_file, os.R_OK))

    @property
    def decoder_kwargs(self):
        """
        Convenience property to use this Vocabulary with the __init__() method
        of the pocketsphinx.Decoder class.

        Returns:
            A dict containing kwargs for the pocketsphinx.Decoder.__init__()
            method.

        Example:
            decoder = pocketsphinx.Decoder(**vocab_instance.decoder_kwargs,
                                           hmm='/path/to/hmm')

        """
        return {'lm': self.languagemodel_file, 'dict': self.dictionary_file}

    def _compile_vocabulary(self, phrases):
        """
        Compiles the vocabulary to the Pocketsphinx format by creating a
        languagemodel and a dictionary.

        Arguments:
            phrases -- a list of phrases that this vocabulary will contain
        """
        text = " ".join([("<s> %s </s>" % phrase) for phrase in phrases])
        self._logger.debug('Compiling languagemodel...')
        vocabulary = self._compile_languagemodel(text, self.languagemodel_file)
        self._logger.debug('Starting dictionary...')
        self._compile_dictionary(vocabulary, self.dictionary_file)

    def _compile_languagemodel(self, text, output_file):
        """
        Compiles the languagemodel from a text.

        Arguments:
            text -- the text the languagemodel will be generated from
            output_file -- the path of the file this languagemodel will
                           be written to

        Returns:
            A list of all unique words this vocabulary contains.
        """
        with tempfile.NamedTemporaryFile(suffix='.vocab', delete=False) as f:
            vocab_file = f.name

        # Create vocab file from text
        self._logger.debug("Creating vocab file: '%s'", vocab_file)
        cmuclmtk.text2vocab(text, vocab_file)

        # Create language model from text
        self._logger.debug("Creating languagemodel file: '%s'", output_file)
        cmuclmtk.text2lm(text, output_file, vocab_file=vocab_file)

        # Get words from vocab file
        self._logger.debug("Getting words from vocab file and removing it " +
                           "afterwards...")
        words = []
        with open(vocab_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('#') and line not in ('<s>', '</s>'):
                    words.append(line)
        os.remove(vocab_file)

        return words

    def _compile_dictionary(self, words, output_file):
        """
        Compiles the dictionary from a list of words.

        Arguments:
            words -- a list of all unique words this vocabulary contains
            output_file -- the path of the file this dictionary will
                           be written to
        """
        # create the dictionary
        self._logger.debug("Getting phonemes for %d words...", len(words))
        pronounced = g2p.translateWords(words)
        zipped = zip(words, pronounced)
        lines = ["%s %s" % (x, y) for x, y in zipped]

        self._logger.debug("Creating dict file: '%s'", output_file)
        with open(output_file, "w") as f:
            for line in lines:
                f.write("%s\n" % line)


def get_phrases_from_module(module):
    """
    Gets phrases from a module.

    Arguments:
        module -- a module reference

    Returns:
        The list of phrases in this module.
    """
    return module.WORDS if hasattr(module, 'WORDS') else []


def get_all_phrases():
    """
    Gets phrases from all modules.

    Returns:
        A list of phrases in all modules plus additional phrases passed to this
        function.
    """
    phrases = []

    modules = brain.Brain.get_modules()
    for module in modules:
        phrases.extend(get_phrases_from_module(module))

    return sorted(list(set(phrases)))

if __name__ == '__main__':
    import shutil
    import argparse

    parser = argparse.ArgumentParser(description='Vocabcompiler Demo')
    parser.add_argument('--base-dir', action='store',
                        help='the directory in which the vocabulary will be ' +
                             'compiled.')
    parser.add_argument('--debug', action='store_true',
                        help='show debug messages')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    base_dir = args.base_dir if args.base_dir else tempfile.mkdtemp()

    phrases = get_all_phrases()
    print "Module phrases:    %r" % phrases

    for subclass in AbstractVocabulary.__subclasses__():
        if hasattr(subclass, 'PATH_PREFIX'):
            vocab = subclass(path=base_dir)
            print("Vocabulary in:     %s" % vocab.path)
            print("Revision file:     %s" % vocab.revision_file)
            print("Compiled revision: %s" % vocab.compiled_revision)
            print("Is compiled:       %r" % vocab.is_compiled)
            print("Matches phrases:   %r" % vocab.matches_phrases(phrases))
            if not vocab.is_compiled or not vocab.matches_phrases(phrases):
                print("Compiling...")
                vocab.compile(phrases)
                print("")
                print("Vocabulary in:     %s" % vocab.path)
                print("Revision file:     %s" % vocab.revision_file)
                print("Compiled revision: %s" % vocab.compiled_revision)
                print("Is compiled:       %r" % vocab.is_compiled)
                print("Matches phrases:   %r" % vocab.matches_phrases(phrases))
                print("")
    if not args.base_dir:
        print("Removing temporary directory '%s'..." % base_dir)
        shutil.rmtree(base_dir)
