#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import xml.sax
import re
import random
import unittest

#
# big phoneme table
#
# entries:
# ( IPA, XSAMPA, MARY )
#

MAX_PHONEME_LENGTH = 2

big_phoneme_table = [

        #
        # stop
        #

        ( u'p' , 'p' , 'p' ),
        ( u'b' , 'b' , 'b' ),
        ( u't' , 't' , 't' ),
        ( u'd' , 'd' , 'd' ),
        ( u'k' , 'k' , 'k' ),
        ( u'g' , 'g' , 'g' ),
        ( u'ʔ' , '?' , '?' ),

        #
        # 2 consonants
        #

        ( u'pf' , 'pf' , 'pf' ),
        ( u'ts' , 'ts' , 'ts' ),
        ( u'tʃ' , 'tS' , 'tS' ),
        ( u'dʒ' , 'dZ' , 'dZ' ),

        #
        # fricative
        #

        ( u'f' , 'f' , 'f' ),
        ( u'v' , 'v' , 'v' ),
        ( u'θ' , 'T' , 'T' ),
        ( u'ð' , 'D' , 'D' ),
        ( u's' , 's' , 's' ),
        ( u'z' , 'z' , 'z' ),
        ( u'ʃ' , 'S' , 'S' ),
        ( u'ʒ' , 'Z' , 'Z' ),
        ( u'ç' , 'C' , 'C' ),
        ( u'j' , 'j' , 'j' ),
        ( u'x' , 'x' , 'x' ),
        ( u'ʁ' , 'R' , 'R' ),
        ( u'h' , 'h' , 'h' ),
        ( u'ɥ' , 'H' , 'H' ),

        #
        # nasal
        #

        ( u'm' , 'm' , 'm' ),
        ( u'n' , 'n' , 'n' ),
        ( u'ɳ' , 'N' , 'N' ),

        #
        # liquid
        #

        ( u'l' , 'l' , 'l' ),
        ( u'r' , 'r' , 'r' ),

        #
        # glide
        #

        ( u'w' , 'w' , 'w' ),
        # see above ( u'j' , 'j' , 'j' ),

        #
        # vowels: monophongs
        #

        # front
        ( u'i' , 'i' , 'i' ),
        ( u'ɪ' , 'I' , 'I' ),
        ( u'y' , 'y' , 'y' ),
        ( u'ʏ' , 'Y' , 'Y' ),
        ( u'e' , 'e' , 'e' ),
        ( u'ø' , '2' , '2' ),
        ( u'œ' , '9' , '9' ),
        ( u'ɛ' , 'E' , 'E' ),
        ( u'æ' , '{' , '{' ),
        ( u'a' , 'a' , 'a' ),

        # central
        ( u'ʌ' , 'V' , 'V' ),
        ( u'ə' , '@' , '@' ),
        ( u'ɐ' , '6' , '6' ),
        ( u'ɜ' , '3' , 'r=' ),

        # back
        ( u'u' , 'u' , 'u' ),
        ( u'ʊ' , 'U' , 'U' ),
        ( u'o' , 'o' , 'o' ),
        ( u'ɔ' , 'O' , 'O' ),
        ( u'ɑ' , 'A' , 'A' ),
        ( u'ɒ' , 'Q' , 'Q' ),

        # diphtongs

        ( u'aɪ' , 'aI' , 'aI' ),
        ( u'ɔɪ' , 'OI' , 'OI' ),
        ( u'aʊ' , 'aU' , 'aU' ),
        ( u'ɔʏ' , 'OY' , 'OY' ),

        #
        # misc
        #
        ( u'ː' , ':' , ':' ),
        ( u'-' , '-' , '-' ),
        ( u'\'' , '\'' , '\'' ),
    ]

IPA_normalization = {
        u':' : u'ː',
        u'?' : u'ʔ',
        u'ɾ' : u'ʁ',
        u'ɡ' : u'g',
        u'ŋ' : u'ɳ',
        u' ' : None,
        u'(' : None,
        u')' : None,
        u'\u02c8' : u'\'',
        u'\u032f' : None,
        u'\u0329' : None,
        u'\u02cc' : None,
        u'\u200d' : None,
        u'\u0279' : None,
    }

XSAMPA_normalization = {
    ' ': None,
    '~': None,
    '0': 'O',
    ',': None,
    }

def _normalize (s, norm_table):

    buf = ""

    for c in s:

        if c in norm_table:
            
            x = norm_table[c]
            if x:
                buf += x
        else:
            buf += c

    return buf

def _translate (graph, s, f_idx, t_idx, spaces=False):

    buf = ""
    i = 0
    l = len(s)

    while i < l:

        found = False

        for pl in range(MAX_PHONEME_LENGTH, 0, -1):

            if i + pl > l:
                continue

            substr = s[i : i+pl ]

            #print u"i: %s, pl: %d, substr: '%s'" % (i, pl, substr)

            for pe in big_phoneme_table:
                p_f = pe[f_idx]
                p_t = pe[t_idx]

                if substr == p_f:
                    buf += p_t
                    i += pl
                    if i<l and s[i] != u'ː' and spaces:
                        buf += ' '
                    found = True
                    break

            if found:
                break

        if not found:

            p = s[i]
            
            msg = (u"_translate: %s: %s Phoneme not found: %s (%s)" % (graph, s, p, repr(p))).encode('UTF8')

            raise Exception (msg)

    return buf

def ipa2xsampa (graph, ipas, spaces=False):
    ipas = _normalize (ipas,  IPA_normalization)
    return _translate (graph, ipas, 0, 1, spaces)

def ipa2mary (graph, ipas):
    ipas = _normalize (ipas,  IPA_normalization)
    return _translate (graph, ipas, 0, 2)

def xsampa2ipa (graph, xs):
    xs = _normalize (xs,  XSAMPA_normalization)
    return _translate (graph, xs, 1, 0)

def mary2ipa (graph, ms):
    ms = _normalize (ms,  XSAMPA_normalization)
    return _translate (graph, ms, 2, 0)

#
# X-ARPABET is my own creation - similar to arpabet plus
# some of my own creating for those phones defined in
#
# http://www.dev.voxforge.org/projects/de/wiki/PhoneSet
#
# uses only latin alpha chars
#

xs2xa_table = [

    #
    # stop
    #

    ('p'  , 'P'),
    ('b'  , 'B'),
    ('t'  , 'T'),
    ('d'  , 'D'),
    ('k'  , 'K'),
    ('g'  , 'G'),
    ('?'  , 'Q'),

    #
    # 2 consonants
    #

    ('pf'  , 'PF'),
    ('ts'  , 'TS'),
    ('tS'  , 'CH'),
    ('dZ'  , 'JH'),

    #
    # fricative
    #

    ('f'  , 'F'),
    ('v'  , 'V'),
    ('T'  , 'TH'),
    ('D'  , 'DH'),
    ('s'  , 'S'),
    ('z'  , 'Z'),
    ('S'  , 'SH'),
    ('Z'  , 'ZH'),
    ('C'  , 'CC'),
    ('j'  , 'Y'),
    ('x'  , 'X'),
    ('R'  , 'RR'),
    ('h'  , 'HH'),
    ('H'  , 'HHH'),

    #
    # nasal
    #

    ('m'  , 'M'),
    ('n'  , 'N'),
    ('N'  , 'NG'),

    #
    # liquid
    #

    ('l'  , 'L'),
    ('r'  , 'R'),

    #
    # glide
    #

    ('w'  , 'W'),

    #
    # vowels, monophongs
    #

    # front
    ('i'  , 'IY'),
    ('i:' , 'IIH'),
    ('I'  , 'IH'),
    ('y'  , 'UE'),
    ('y:' , 'YYH'),
    ('Y'  , 'YY'),
    ('e'  , 'EE'),
    ('e:' , 'EEH'),
    ('2'  , 'OH'),
    ('2:' , 'OHH'),
    ('9'  , 'OE'),
    ('E'  , 'EH'),
    ('E:' , 'EHH'),
    ('{'  , 'AE'),
    ('{:' , 'AEH'),
    ('a'  , 'AH'),
    ('a:' , 'AAH'),
    ('3'  , 'ER'),
    ('3:' , 'ERH'),

    # central
    ('V'  , 'VV'),
    ('@'  , 'AX'),
    ('6'  , 'EX'),
    #('3'  , 'AOR'),

    # back
    ('u'  , 'UH'),
    ('u:' , 'UUH'),
    ('U'  , 'UU'),
    ('o'  , 'AO'),
    ('o:' , 'OOH'),
    ('O'  , 'OO'),
    ('O:' , 'OOOH'),
    ('A'  , 'AA'),
    ('A:' , 'AAAH'),
    ('Q'  , 'QQ'),

    # diphtongs
    ('aI'  , 'AY'),
    ('OI'  , 'OI'),
    ('aU'  , 'AW'),
    ('OY'  , 'OY'),
    ]

XARPABET_normalization = {
    '-': None,
    '\'': None,
    }

def xsampa2xarpabet (graph, s):
    s = _normalize (s,  XARPABET_normalization)

    buf = ""
    i = 0
    l = len(s)

    while i < l:

        found = False

        for pl in range(MAX_PHONEME_LENGTH, 0, -1):

            if i + pl > l:
                continue

            substr = s[i : i+pl ]

            #print u"i: %s, pl: %d, substr: '%s'" % (i, pl, substr)

            for pe in xs2xa_table:
                p_f = pe[0]
                p_t = pe[1]

                if substr == p_f:
                    if len(buf)>0:
                        buf += ' '
                    buf += p_t
                    i += pl
                    found = True
                    break

            if found:
                break

        if not found:

            p = s[i]

            msg = u"xsampa2xarpabet: graph:'%s' - s:'%s' Phoneme not found: '%s' (%d) '%s'" % (graph, s, p, ord(p), s[i:])

            raise Exception (msg.encode('UTF8'))

    return buf

class TestPhoneticAlphabets (unittest.TestCase):

    def setUp(self):
        self.seq = range(10)

    def test_ipa(self):

        res = ipa2xsampa ("EISENBAHN", u"ˈaɪ̯zən̩ˌbaːn")
        #print "res: %s" % res
        self.assertEqual (res, "'aIz@nba:n")

        res = ipa2xsampa ("DIPHTONGTEST", u"aɪɔɪaʊɜ'")
        #print "res: %s" % res
        self.assertEqual (res, "aIOIaU3'")

        res = ipa2mary ("EISENBAHN", u"ˈaɪ̯zən̩ˌbaːn")
        #print "res: %s" % res
        self.assertEqual (res, "'aIz@nba:n")

        res = ipa2mary ("DIPHTONGTEST", u"aɪɔɪaʊɜ'")
        #print "res: %s" % res
        self.assertEqual (res, "aIOIaUr='")

    def test_xarpa(self):

        res = xsampa2xarpabet ("JAHRHUNDERTE", "ja:6-'hUn-d6-t@")
        #print "res: %s" % res
        self.assertEqual (res, "Y AAH EX HH UU N D EX T AX")

        res = xsampa2xarpabet ("ABGESCHRIEBEN", "'ap-g@-SRi:-b@n")
        #print "res: %s" % res
        self.assertEqual (res, "AH P G AX SH RR IIH B AX N")

        res = xsampa2xarpabet ("ZUGEGRIFFEN", "'tsu:-g@-gRI-f@n")
        #print "res: %s" % res
        self.assertEqual (res, "TS UUH G AX G RR IH F AX N")

        res = xsampa2xarpabet ("AUSLEGUNG", "'aU-sle:-gUN")
        #print "res: %s" % res
        self.assertEqual (res, "AW S L EEH G UU NG")

    def test_xarpa_unique(self):

        # all xarpa transcriptions have to be unique

        uniq_xs = set()
        uniq_xa = set()

        for entry in xs2xa_table:
            xs = entry[0]
            xa = entry[1]
            #print (u"xs: %s, xa: %s" % (xs, xa)).encode('utf8')
            self.assertFalse (xa in uniq_xa)
            uniq_xa.add(xa)
            self.assertFalse (xs in uniq_xs)
            uniq_xs.add(xs)
        


if __name__ == "__main__":

    unittest.main()

