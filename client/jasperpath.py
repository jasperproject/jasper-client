#!/usr/bin/env python2
# -*- coding: utf-8-*-
import os
JASPER_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir))
DATA_PATH = os.path.join(JASPER_PATH, "static")
CLIENTMODULES_PATH = os.path.join(JASPER_PATH, "client", "modules")

CONFIG_PATH = os.path.expanduser(os.getenv('JASPER_CONFIG','~/.jasper-client'))
VOCAB_PATH = os.path.join(CONFIG_PATH, "vocab")

def _getprefix(name):
	prefixes = ('/usr/share','/usr/local/share','/opt')
	for prefix in prefixes:
		path = os.path.join(prefix,name)
		if os.path.exists(path):
			return path
	raise OSError("Could not find '%s'. Are you sure it's installed?")

PHONETISAURUS_PATH = _getprefix('phonetisaurus')
PHONETISAURUS_SCRIPTS_PATH = os.path.join(PHONETISAURUS_PATH,"scripts")

HMM_PATH = os.path.join(_getprefix('pocketsphinx'),'model/hmm/en_US/hub4wsj_sc_8k')

def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)

def vocab(*fname):
	return os.path.join(VOCAB_PATH, *fname)

def data(*fname):
    return os.path.join(DATA_PATH, *fname)

def phonetisaurus(*fname):
	return os.path.join(PHONETISAURUS_PATH, *fname)

def cmucslmtk(*fname):
	return os.path.join(CMUCSLMTK_PATH, *fname)

def clientmodules(*fname):
	return os.path.join(CLIENTMODULES_PATH, *fname)