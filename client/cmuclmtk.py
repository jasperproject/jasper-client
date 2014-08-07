#!/usr/bin/env python
# -*- coding: utf-8-*-
#
# Copyright (c) 2014, Jan Holthuis
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
    Wrapper class for accessing the cmuclmtk tools.
"""

import os
import io
import tempfile
import subprocess
import shutil

# TODO: add wrapper functions for tools
#  text2wngram
#  ngram2mgram
#  wngram2idngram
#  idngram2stats
#  mergeidngram
#  binlm2arpa
#  evallm
#  interpolate

class BaseError(Exception):
    pass
class ConversionError(BaseError):
    pass

def text2wfreq(text, output_file, hashtablesize=1000000, verbosity=2):
    """
        List of every word which occurred in the text, along with its number of occurrences.
        Notes : Uses a hash-table to provide an efficient method of counting word occurrences. Output list is not sorted (due to "randomness" of the hash-table), but can be easily sorted into the user's desired order by the UNIX sort command. In any case, the output does not need to be sorted in order to serve as input for wfreq2vocab. Higher values for the hashtablesize parameter require more memory, but can reduce computation time.
    """
    cmd = ['text2wfreq', '-hash', hashtablesize,
                         '-verbosity', verbosity]

    # Ensure that every parameter is of type 'str'
    cmd = [str(x) for x in cmd]

    with tempfile.SpooledTemporaryFile(mode='w+') as input_f:
        input_f.write(text)
        input_f.seek(0)
        with open(output_file,'w+') as output_f:
            exitcode = subprocess.call(cmd, stdin=input_f, stdout=output_f)

    if exitcode != 0:
        raise ConversionError("'%s' returned with non-zero exit status '%s'" % (cmd[0], exitcode))

def wfreq2vocab(wfreq_file, output_file, top=None, gt=None, records=1000000, verbosity=2):
    """
        Takes a a word unigram file, as produced by text2wfreq and converts it to a vocabulary file.
        The top parameter allows the user to specify the size of the vocabulary; if the function is called with the parameter top=20000, then the vocabulary will consist of the most common 20,000 words.
        The gt parameter allows the user to specify the number of times that a word must occur to be included in the vocabulary; if the function is called with the parameter gt=10, then the vocabulary will consist of all the words which occurred more than 10 times.
        If neither the gt, nor the top parameters are specified, then the function runs with the default setting of taking the top 20,000 words.
        The records parameter (default: 1000000) allows the user to specify how many of the word and count records to allocate memory for. If the number of words in the input exceeds this number, then the function will fail and raise a ConversionError, but a high number will obviously result in a higher memory requirement.
    """
    cmd = ['wfreq2vocab', '-verbosity', verbosity,
                           '-records', records]

    # Ensure that every parameter is of type 'str'
    cmd = [str(x) for x in cmd]

    if top:
        cmd.extend(['-top',top])
    elif gt:
        cmd.extend(['-gt',gt])

    with open(wfreq_file,'r') as input_f:
        with open(output_file,'w+') as output_f:
            exitcode = subprocess.call(cmd, stdin=input_f, stdout=output_f)

    if exitcode != 0:
        raise ConversionError("'%s' returned with non-zero exit status '%s'" % (cmd[0], exitcode))


def text2vocab_file(text, output_file, text2wfreq_kwargs={}, wfreq2vocab_kwargs={}):
    """
        Convienience function that uses text2wfreq and wfreq2vocab to create a vocabulary file from text.
    """
    with tempfile.NamedTemporaryFile(suffix='.wfreq', delete=False) as f:
        wfreq_file = f.name

    try:
        text2wfreq(text, wfreq_file, **text2wfreq_kwargs)
        wfreq2vocab(wfreq_file, output_file, **wfreq2vocab_kwargs)
    except ConversionError:
        raise
    finally:
        os.remove(wfreq_file)


def text2idngram(text, vocab_file, output_file, buffersize=100, hashtablesize=2000000, files=20, compress=False, verbosity=2, n=3, write_ascii=False, fof_size=10):
    """
        Takes a text stream, plus a vocabulary file, and outputs an idngram file (a ist of every id n-gram which occurred in the text, along with its number of occurrences)
        Notes : Maps each word in the text stream to a short integer as soon as it has been read, thus enabling more n-grams to be stored and sorted in memory.
        By default, the id n-gram file is written out as binary file, unless the parameter write_ascii is set to True.
        The size of the buffer which is used to store the n-grams can be specified using the buffersize parameter. This value is in megabytes, and the default value can be changed from 100 by changing the value of STD_MEM in the file src/toolkit.h before compiling the toolkit.
        The function will also report the frequency of frequency of n-grams, and the corresponding recommended value for the spec_num parameters of idngram2lm. The fof_size parameter allows the user to specify the length of this list. A value of 0 will result in no list being displayed.
        In the case of really huge quantities of data, it may be the case that more temporary files are generated than can be opened at one time by the filing system. In this case, the temporary files will be merged in chunks, and the files parameter can be used to specify how many files are allowed to be open at one time.
    """
    cmd = ['text2idngram', '-vocab', vocab_file,
                           '-idngram', output_file,
                           '-buffer', buffersize,
                           '-hash', hashtablesize,
                           '-files', files,
                           '-verbosity',verbosity,
                           '-n',n,
                           '-fof_size',fof_size]

    # Save CWD
    curdir = os.getcwd()
    # Go into tempdir
    tempdir = tempfile.mkdtemp(prefix='cmuclmtk-')
    os.chdir(tempdir)

    if compress:
        cmd.append('-compress')
    if write_ascii:
        cmd.append('-write_ascii')

    # Ensure that every parameter is of type 'str'
    cmd = [str(x) for x in cmd]
    
    with tempfile.SpooledTemporaryFile() as input_f:
        input_f.write(text)
        input_f.seek(0)
        with tempfile.SpooledTemporaryFile() as output_f:
            exitcode = subprocess.call(cmd, stdin=input_f, stdout=output_f)
            output = output_f.read()

    # Go back and throw away tempdir
    os.chdir(curdir)
    shutil.rmtree(tempdir)

    if exitcode != 0:
        raise ConversionError("'%r' returned with non-zero exit status '%s'" % (cmd, exitcode))

    return output


def idngram2lm(idngram_file, vocab_file, output_file, context_file=None, vocab_type=1, oov_fraction=0.5, four_byte_counts=False, min_unicount=0, zeroton_fraction=False, n=3, verbosity=2, arpa_output=True, ascii_input=False):
    """
        Takes an idngram-file (in either binary (by default) or ASCII (if specified) format), a vocabulary file, and (optionally) a context cues file. Additional command line parameters will specify the cutoffs, the discounting strategy and parameters, etc. It outputs a language model, in either binary format (to be read by evallm), or in ARPA format.
    """
     # TODO: Args still missing
     # [ -calc_mem | -buffer 100 | -spec_num y ... z ]
     # [ -two_byte_bo_weights   
     #     [ -min_bo_weight nnnnn] [ -max_bo_weight nnnnn] [ -out_of_range_bo_weights] ]
     # [ -linear | -absolute | -good_turing | -witten_bell ]
     # [ -disc_ranges 1 7 7 ]
     # [ -cutoffs 0 ... 0 ]

    cmd = ['idngram2lm', '-idngram', idngram_file,
                         '-vocab', vocab_file,
                         '-vocab_type', vocab_type,
                         '-oov_fraction', oov_fraction,
                         '-min_unicount',min_unicount,
                         '-verbosity',verbosity,
                         '-n',n]
    if arpa_output:
        cmd.extend(['-arpa',output_file])
    else:
        cmd.extend(['-binary',output_file])

    if four_byte_counts:
        cmd.append('-four_byte_counts')

    if zeroton_fraction:
        cmd.append('-zeroton_fraction')

    if ascii_input:
        cmd.append('-ascii_input')
    else:
        cmd.append('-bin_input')

    # Ensure that every parameter is of type 'str'
    cmd = [str(x) for x in cmd]

    with tempfile.SpooledTemporaryFile() as output_f:
        exitcode = subprocess.call(cmd, stdout=output_f)
        output = output_f.read()
    print output

    if exitcode != 0:
        raise ConversionError("'%s' returned with non-zero exit status '%s'" % (cmd[0], exitcode))

    return output

def text2lm(text, output_file, vocab_file=None, text2idngram_kwargs={}, idngram2lm_kwargs={}):
    """
        Convienience function to directly convert text (and vocabulary) into a language model (using .
    """
    if vocab_file:
        used_vocab_file = vocab_file
    else:
        # Create temporary vocab file
        with tempfile.NamedTemporaryFile(suffix='.vocab', delete=False) as f:
            used_vocab_file = f.name
        text2vocab_file(text, used_vocab_file)

    # Create temporary idngram file
    with tempfile.NamedTemporaryFile(suffix='.idngram', delete=False) as f:
        idngram_file = f.name

    try:
        output1 = text2idngram(text, vocab_file=used_vocab_file, output_file=idngram_file, **text2idngram_kwargs)
        output2 = idngram2lm(idngram_file, vocab_file=used_vocab_file, output_file=output_file, **idngram2lm_kwargs)
    except ConversionError:
        output = (None, None)
        raise
    else:
        output = (output1, output2)
    finally:
        # Remove temporary files
        if not vocab_file:
            os.remove(used_vocab_file)
        os.remove(idngram_file)
    return output
