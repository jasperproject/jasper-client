# -*- coding: utf-8 -*-
"""
Iterates over all the WORDS variables in the modules and creates a
vocabulary for the respective stt_engine if needed.
"""

import os
import logging
import hashlib
import shutil


def phrases_to_revision(phrases):
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


class VocabularyCompiler(object):
    """
    Generic vocabulary compiler vocabulary compiler.
    """

    def __init__(self, folder, name='default', path='.'):
        """
        Initializes a new Vocabulary instance.

        Optional Arguments:
            name -- (optional) the name of the vocabulary (Default: 'default')
            path -- (optional) the path in which the vocabulary exists or will
                    be created (Default: '.')
        """
        self.name = name
        self.path = os.path.abspath(os.path.join(path, folder, name))
        self._logger = logging.getLogger(__name__)

    @property
    def revision_file(self):
        """
        Returns:
            The path of the the revision file as string
        """
        return os.path.join(self.path, 'revision')

    @property
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
        return (self.compiled_revision == phrases_to_revision(phrases))

    def compile(self, config, compilation_func, phrases, force=False):
        """
        Compiles this vocabulary. If the force argument is True, compilation
        will be forced regardless of necessity (which means that the
        preliminary check if the current revision already equals the
        revision after compilation will be skipped).

        Arguments:
            phrases -- a list of phrases that this vocabulary will contain
            force -- (optional) forces compilation (Default: False)

        Returns:
            The revision of the compiled vocabulary
        """
        revision = phrases_to_revision(phrases)
        debug = self._logger.getEffectiveLevel() == logging.DEBUG
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
                                   self.path, exc_info=debug)
                raise
        try:
            with open(self.revision_file, 'w') as f:
                f.write(revision)
        except (OSError, IOError):
            self._logger.error("Couldn't write revision file in '%s'",
                               self.revision_file, exc_info=debug)
            raise
        else:
            self._logger.info('Starting compilation...')
            try:
                compilation_func(config, self.path, phrases)
            except Exception as e:
                msg = "Fatal compilation error occured"
                if hasattr(e, 'message') and len(e.message) > 0:
                    msg += ": %s" % e.message
                self._logger.error(msg, exc_info=debug)
                try:
                    os.remove(self.revision_file)
                    shutil.rmtree(self.path)
                except EnvironmentError as e:
                    msg = 'Another error occured while cleaning up'
                    if e.strerror and e.errno:
                        msg = '%s: %s (Errno: %d)' % (msg, e.strerror, e.errno)
                    else:
                        msg = '%s: %r' % (msg, e.args)
                    self._logger.error(msg, exc_info=debug)
                raise e
            else:
                self._logger.info('Compilation done.')
        return revision
