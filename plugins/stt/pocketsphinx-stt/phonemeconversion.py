# -*- coding: utf-8 -*-
import logging

XSAMPA_TO_ARPABET_MAPPING = {
    # stop
    'p': 'P',
    'b': 'B',
    't': 'T',
    'd': 'D',
    'k': 'K',
    'g': 'G',
    '?': 'Q',

    # 2 consonants
    'pf': 'PF',
    'ts': 'TS',
    'tS': 'CH',
    'dZ': 'JH',

    # fricative
    'f': 'F',
    'v': 'V',
    'T': 'TH',
    'D': 'DH',
    's': 'S',
    'z': 'Z',
    'S': 'SH',
    'Z': 'ZH',
    'C': 'CC',
    'j': 'Y',
    'x': 'X',
    'R': 'RR',
    'h': 'HH',
    'H': 'HHH',

    # nasal
    'm': 'M',
    'n': 'N',
    'N': 'NG',

    # liquid
    'l': 'L',
    'r': 'R',

    # glide
    'w': 'W',

    # front vowels
    'i': 'IY',
    'i:': 'IIH',
    'I': 'IH',
    'y': 'UE',
    'y:': 'YYH',
    'Y': 'YY',
    'e': 'EE',
    'e:': 'EEH',
    '2': 'OH',
    '2:': 'OHH',
    '9': 'OE',
    'E': 'EH',
    'E:': 'EHH',
    '{': 'AE',
    '{:': 'AEH',
    'a': 'AH',
    'a:': 'AAH',
    '3': 'ER',
    '3:': 'ERH',

    # central vowels
    'V': 'VV',
    '@': 'AX',
    '6': 'EX',

    # back vowels
    'u': 'UH',
    'u:': 'UUH',
    'U': 'UU',
    'o': 'AO',
    'o:': 'OOH',
    'O': 'OO',
    'O:': 'OOOH',
    'A': 'AA',
    'A:': 'AAAH',
    'Q': 'QQ',

    # diphtongs vowels
    'aI': 'AY',
    'OI': 'OI',
    'aU': 'AW',
    'OY': 'OY',

    # Fuzzy stuff
    'c': 'K',
    'q': 'K'
}

MAX_PHONE_LENGTH = max([len(x) for x in XSAMPA_TO_ARPABET_MAPPING.keys()])


def xsampa_to_arpabet(xsampa_string, sep=' '):
    logger = logging.getLogger(__name__)
    s = xsampa_string.replace('-', '').replace('\'', '').replace(' ', '')
    result = []

    i = 0
    while i < len(s):
        num_remaining_chars = len(s) - i
        phone_length = (MAX_PHONE_LENGTH
                        if MAX_PHONE_LENGTH > num_remaining_chars
                        else num_remaining_chars)

        for j in range(phone_length, 0, -1):
            phone = s[i:i+j]
            if phone in XSAMPA_TO_ARPABET_MAPPING:
                result.append(XSAMPA_TO_ARPABET_MAPPING[phone])
                i += j
                break
        else:
            logger.warning("Phone not found:  '%s'", s[i])
            i += 1

    return sep.join(result)
