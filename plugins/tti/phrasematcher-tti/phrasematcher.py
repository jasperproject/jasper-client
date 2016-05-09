#implementation taken from https://gist.github.com/Holzhaus/cdf3e9534e6295d40e07
import itertools
import string
import re
from jasper import plugin

class PhraseMatcherPlugin(plugin.TTIPlugin):

    @classmethod
    def get_possible_phrases(cls):
        # Sample implementation, there might be a better one
        phrases = []
        for base_phrase, action in cls.ACTIONS:
            placeholders = [x[1] for x in string.Formatter().parse(base_phrase)]
            factors = [placeholder_values[placeholder] for placeholder in placeholders]
            combinations = itertools.product(*factors)
            for combination in combinations:
                replacement_values = dict(zip(placeholders,combination))
                phrases.append(base_phrase.format(**replacement_values))
        return phrases

    @classmethod
    def get_regex_phrases(cls):
        return [cls.base_phrase_to_regex_pattern(base_phrase) for base_phrase, action in cls.ACTIONS]

    @classmethod
    def base_phrase_to_regex_pattern(cls, base_phrase):
        # Sample implementation, I think that this can be improved, too
        placeholders = [x[1] for x in string.Formatter().parse(base_phrase)]
        placeholder_values = {}
        for placeholder in placeholders:
            placeholder_values[placeholder] = '(?P<{}>.+)'.format(placeholder)
        regex_phrase = "^{}$".format(base_phrase.format(**placeholder_values))
        pattern = re.compile(regex_phrase, re.LOCALE | re.UNICODE)
        return pattern

    @classmethod
    def match_phrase(cls, phrase):
        for pattern in cls.get_regex_phrases():
            matchobj = pattern.match(phrase)
            if matchobj:
                return matchobj
        return None

    @classmethod
    def handle_intent(cls, phrase):
        matchobj = cls.match_phrase(phrase)
        if matchobj:
            for base_phrase, action in cls.ACTIONS:
                if matchobj.re.match(base_phrase):
                    kwargs = matchobj.groupdict()
                    action(**kwargs)
                    return True
        return False

#
# Now we create 2 classes that inhert from Phrase Matcher and actually define some phrases/actions
#
#
#class LightController(PhraseMatcher):
#    @classmethod
#    def change_light_color(cls, **kwargs):
#        print("Changing {location} light colors  to {color} now...".format(**kwargs))
#    @classmethod
#    def switch_light_state(cls, **kwargs):
#        print("Switching lights {state} now...".format(**kwargs))
#    WORDS = {'location': ['ALL', 'BEDROOM', 'LIVINGROOM','BATHROOM'],
#             'color': ['BLUE','YELLOW','RED', 'GREEN'],
#             'state': ['ON','OFF']}
# Hack because we can't reference classmethods inside the class definition
#LightController.ACTIONS = [('SWITCH {location} LIGHTS TO COLOR {color}', LightController.change_light_color),
#                           ('SWITCH LIGHTS {state}', LightController.switch_light_state)]#
#
#import time
#class Clock(PhraseMatcher):
#    @classmethod
#    def say_time(cls, **kwargs):
#        print(time.strftime("The time is %H hours and %M minutes."))
#Clock.ACTIONS = [('WHAT TIME IS IT',Clock.say_time)]#
#
#
# Here we define the classes that are going to handle input phrases
#
#
#PLUGINS = [LightController, Clock]#
#
#def handle(phrase):
#    handled = False
#    for plugin in PLUGINS:
#        if plugin.handle(phrase):
#            handled = True
#    if not handled:
#        print("No plugin can handle: '{}'".format(phrase))
#    return handled

#
# Some sample input
#

#sample_phrases = ["SWITCH LIVINGROOM LIGHTS TO COLOR RED",
#                  "WHAT TIME IS IT",
#                  "THIS IS A TEST PHRASE NO PLUGIN UNDERSTANDS",
#                  "SWITCH LIGHTS OFF"]
#
#for phrase in sample_phrases:
#    handle(phrase)
