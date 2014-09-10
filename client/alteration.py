# -*- coding: utf-8-*-
import re


def detectYears(input):
    YEAR_REGEX = re.compile(r'(\b)(\d\d)([1-9]\d)(\b)')
    return YEAR_REGEX.sub('\g<1>\g<2> \g<3>\g<4>', input)


def clean(input):
    """
        Manually adjust output text before it's translated into
        actual speech by the TTS system. This is to fix minior
        idiomatic issues, for example, that 1901 is pronounced
        "one thousand, ninehundred and one" rather than
        "nineteen oh one".

        Arguments:
        input -- original speech text to-be modified
    """
    return detectYears(input)
