#basic implementation taken from https://gist.github.com/Holzhaus/cdf3e9534e6295d40e07
import itertools
import string
import re
from jasper import plugin

class PhraseMatcherPlugin(plugin.TTIPlugin):

    def get_phrases(self):
        # Sample implementation, there might be a better one
        phrases = []
        for base_phrase, action in self.ACTIONS:
            placeholders = [x[1] for x in string.Formatter().parse(base_phrase)]
            factors = [placeholder_values[placeholder] for placeholder in placeholders]
            combinations = itertools.product(*factors)
            for combination in combinations:
                replacement_values = dict(zip(placeholders,combination))
                phrases.append(base_phrase.format(**replacement_values))
        return phrases

    def get_regex_phrases(self):
        return [self.base_phrase_to_regex_pattern(base_phrase) for base_phrase, action in self.ACTIONS]

    def base_phrase_to_regex_pattern(self, base_phrase):
        # Sample implementation, I think that this can be improved, too
        placeholders = [x[1] for x in string.Formatter().parse(base_phrase)]
        placeholder_values = {}
        for placeholder in placeholders:
            placeholder_values[placeholder] = '(?P<{}>.+)'.format(placeholder)
        regex_phrase = "^{}$".format(base_phrase.format(**placeholder_values))
        pattern = re.compile(regex_phrase, re.LOCALE | re.UNICODE)
        return pattern

    def match_phrase(self, phrase):
        for pattern in self.get_regex_phrases():
            matchobj = pattern.match(phrase)
            if matchobj:
                return matchobj
        return None

    def is_valid(self, phrase):
        matchobj = self.match_phrase(phrase)
        if matchobj:
            return True
        return False

    def get_confidence(self, phrase):
        return is_valid(self, phrase)

    def get_actionlist(self, phrase):
        pass

    def get_intent(self, phrase):
        matchobj = self.match_phrase(phrase)
        if matchobj:
            for base_phrase, action in self.ACTIONS:
                if matchobj.re.match(base_phrase):
                    kwargs = matchobj.groupdict()
                    #action(**kwargs)                   
                    return [action, kwargs]
        return [None,  None]

    def handle_intent(self, phrase):
        matchobj = self.match_phrase(phrase)
        if matchobj:
            for base_phrase, action in self.ACTIONS:
                if matchobj.re.match(base_phrase):
                    kwargs = matchobj.groupdict()                    
                    action(**kwargs)
                    return True
        return False
