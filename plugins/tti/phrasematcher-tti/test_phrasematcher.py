# -*- coding: utf-8 -*-
import unittest
import time
from jasper import testutils
from . import phrasematcher

#
# Some sample input
#

sample_phrases = [("LightController",  "SWITCH LIVINGROOM LIGHTS TO COLOR RED"),
                                ("Clock", "WHAT TIME IS IT"),
                                ("None", "THIS IS A TEST PHRASE NO PLUGIN UNDERSTANDS"),
                                ("LightController", "SWITCH LIGHTS OFF")]

class LightController():
    
    def __init__(self, mic):
        self._mic = mic
        self._tti=testutils.get_genericplugin_instance(phrasematcher.PhraseMatcherPlugin)
        self._tti.WORDS = {'location': ['ALL', 'BEDROOM', 'LIVINGROOM','BATHROOM'],
                                        'color': ['BLUE','YELLOW','RED', 'GREEN'],
                                        'state': ['ON','OFF']}
        self._tti.ACTIONS = [('SWITCH {location} LIGHTS TO COLOR {color}', LightController.change_light_color),
                                        ('SWITCH LIGHTS {state}', LightController.switch_light_state)]

    def change_light_color(self, **kwargs):
        self._mic.say("Changing {location} light colors  to {color} now...".format(**kwargs))

    def switch_light_state(self, **kwargs):
        self._mic.say("Switching lights {state} now...".format(**kwargs))
        
    def handle(self, phrase):
        action, param = self._tti.get_intent(phrase)
        if action:
            action(self, **param)
        
    def is_valid(self, phrase):
        self._tti.is_valid(phrase)        
        
    def name(self):
        return "LightController"

class Clock():
   
    def __init__(self,  mic):
        self._mic = mic
        self._tti=testutils.get_genericplugin_instance(phrasematcher.PhraseMatcherPlugin)
        self._tti.ACTIONS = [('WHAT TIME IS IT',Clock.say_time)]#

    def say_time(self, **kwargs):
        self._mic.say(time.strftime("The time is %H hours and %M minutes."))
        
    def handle(self, phrase):
        action, param = self._tti.get_intent(phrase)
        if action:
            action(self, **param)
        
    def is_valid(self, phrase):
        self._tti.is_valid(phrase)    

    def name(self):
        return "Clock"        

class TestPhrasematcherPlugin(unittest.TestCase):
    def setUp(self):
        self.mic = testutils.TestMic()
        self.plugins = [LightController(self.mic), Clock(self.mic)]   
   
    def handle(self, phrase):
        handled = False
        for plugin in self.plugins:
            if plugin.handle(phrase):
                handled = True        
        return handled   

    def test_is_valid_method(self): 
        for plugin in self.plugins:    
            for pluginname,  phrase in sample_phrases:
                if pluginname == plugin.name:
                    self.assertTrue(plugin.is_valid(phrase))
                else:
                     self.assertFalse(plugin.is_valid(phrase))

    def test_handle_method(self):        
        for pluginname,  phrase in sample_phrases:
            self.handle(phrase) 
        self.assertEqual(len(self.mic.outputs), 3)
        #print self.mic.outputs
