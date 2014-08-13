#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
JASPER_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
DATA_PATH = os.path.join(JASPER_PATH, "static")
CLIENTMODULES_PATH = os.path.join(JASPER_PATH, "client", "modules")

CONFIG_PATH = os.path.expanduser(os.getenv('JASPER_CONFIG', '~/.jasper-client'))

def _getprefix(name):
    prefixes = ('/usr/share', '/usr/local/share', '/opt')
    for prefix in prefixes:
        path = os.path.join(prefix, name)
        if os.path.exists(path):
            return path
    raise OSError("Could not find '%s'. Are you sure it's installed?")

PHONETISAURUS_PATH = _getprefix('phonetisaurus')
PHONETISAURUS_SCRIPTS_PATH = os.path.join(PHONETISAURUS_PATH, "scripts")

HMM_PATH = os.path.join(_getprefix('pocketsphinx'), 'model/hmm/en_US/hub4wsj_sc_8k')

def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)

def languagemodel(name="default", static=False):
    components = ("languagemodels", "%s.lm" % name)
    if static:
        path = data(*components)
    else:
        path = config(*components)
    return path

def dictionary(name="default", static=False):
    components = ("dictionaries", "%s.dic" % name)
    if static:
        path = data(*components)
    else:
        path = config(*components)
    return path

def data(*fname):
    return os.path.join(DATA_PATH, *fname)

def phonetisaurus(*fname):
    return os.path.join(PHONETISAURUS_PATH, *fname)

def cmucslmtk(*fname):
    return os.path.join(CMUCSLMTK_PATH, *fname)

def clientmodules(*fname):
    return os.path.join(CLIENTMODULES_PATH, *fname)
