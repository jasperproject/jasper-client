# -*- coding: utf-8 -*-
import os

# Jasper main directory
PKG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)))

APP_PATH = os.path.normpath(os.path.join(PKG_PATH, os.pardir))
DATA_PATH = os.path.join(PKG_PATH, "data")
PLUGIN_PATH = os.path.join(APP_PATH, "plugins")

CONFIG_PATH = os.path.expanduser(os.getenv('JASPER_CONFIG', '~/.jasper'))


def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)


def data(*fname):
    return os.path.join(DATA_PATH, *fname)
