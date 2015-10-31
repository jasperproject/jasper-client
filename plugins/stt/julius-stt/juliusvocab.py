# -*- coding: utf-8 -*-
import re
import contextlib
import tarfile
import os
import logging
import tempfile
import shutil
import subprocess
import jasperpath


class VoxForgeLexicon(object):
    def __init__(self, fname, membername=None):
        self._dict = {}
        self.parse(fname, membername)

    @contextlib.contextmanager
    def open_dict(self, fname, membername=None):
        if tarfile.is_tarfile(fname):
            if not membername:
                raise ValueError('archive membername not set!')
            tf = tarfile.open(fname)
            f = tf.extractfile(membername)
            yield f
            f.close()
            tf.close()
        else:
            with open(fname) as f:
                yield f

    def parse(self, fname, membername=None):
        pattern = re.compile(r'\[(.+)\]\W(.+)')
        with self.open_dict(fname, membername=membername) as f:
            for line in f:
                matchobj = pattern.search(line)
                if matchobj:
                    word, phoneme = [x.strip() for x in matchobj.groups()]
                    if word in self._dict:
                        self._dict[word].append(phoneme)
                    else:
                        self._dict[word] = [phoneme]

    def translate_word(self, word):
        if word in self._dict:
            return self._dict[word]
        else:
            return []


def get_dfa_path(path):
    """
    Returns:
        The path of the the julius dfa file as string
    """
    return os.path.join(path, 'dfa')


def get_dict_path(path):
    """
    Returns:
        The path of the the julius dict file as string
    """
    return os.path.join(path, 'dict')


def get_grammar(phrases):
    return {'S': [['NS_B', 'WORD_LOOP', 'NS_E']],
            'WORD_LOOP': [['WORD_LOOP', 'WORD'], ['WORD']]}


def get_word_defs(lexicon, phrases):
    word_defs = {'NS_B': [('<s>', 'sil')],
                 'NS_E': [('</s>', 'sil')],
                 'WORD': []}

    words = []
    for phrase in phrases:
        if ' ' in phrase:
            for word in phrase.split(' '):
                words.append(word)
        else:
            words.append(phrase)

    for word in words:
        for phoneme in lexicon.translate_word(word):
            word_defs['WORD'].append((word, phoneme))
    return word_defs


def compile_vocabulary(directory, phrases, profile):
    logger = logging.getLogger(__name__)
    prefix = 'jasper'
    tmpdir = tempfile.mkdtemp()

    lexicon_file = jasperpath.data('julius-stt', 'VoxForge.tgz')
    lexicon_archive_member = 'VoxForge/VoxForgeDict'
    if 'julius' in profile:
        if 'lexicon' in profile['julius']:
            lexicon_file = profile['julius']['lexicon']
        if 'lexicon_archive_member' in profile['julius']:
            lexicon_archive_member = \
                profile['julius']['lexicon_archive_member']

    lexicon = VoxForgeLexicon(lexicon_file, lexicon_archive_member)

    # Create grammar file
    tmp_grammar_file = os.path.join(tmpdir,
                                    os.extsep.join([prefix, 'grammar']))
    with open(tmp_grammar_file, 'w') as f:
        grammar = get_grammar(phrases)
        for definition in grammar.pop('S'):
            f.write("%s: %s\n" % ('S', ' '.join(definition)))
        for name, definitions in grammar.items():
            for definition in definitions:
                f.write("%s: %s\n" % (name, ' '.join(definition)))

    # Create voca file
    tmp_voca_file = os.path.join(tmpdir, os.extsep.join([prefix, 'voca']))
    with open(tmp_voca_file, 'w') as f:
        for category, words in get_word_defs(lexicon, phrases).items():
            f.write("%% %s\n" % category)
            for word, phoneme in words:
                f.write("%s\t\t\t%s\n" % (word, phoneme))

    # mkdfa.pl
    olddir = os.getcwd()
    os.chdir(tmpdir)
    cmd = ['mkdfa.pl', str(prefix)]
    with tempfile.SpooledTemporaryFile() as out_f:
        subprocess.call(cmd, stdout=out_f, stderr=out_f)
        out_f.seek(0)
        for line in out_f.read().splitlines():
            line = line.strip()
            if line:
                logger.debug(line)
    os.chdir(olddir)

    tmp_dfa_file = os.path.join(tmpdir, os.extsep.join([prefix, 'dfa']))
    tmp_dict_file = os.path.join(tmpdir, os.extsep.join([prefix, 'dict']))
    shutil.move(tmp_dfa_file, get_dfa_path(directory))
    shutil.move(tmp_dict_file, get_dict_path(directory))

    shutil.rmtree(tmpdir)
