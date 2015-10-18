#!/usr/bin/env python2
# -*- coding: utf-8-*-

import os
import sys
import shutil
import logging

import yaml
import argparse

from client import tts, stt, jasperpath, diagnose, audioengine, brain
from client import pluginstore
from client.conversation import Conversation

# Add jasperpath.LIB_PATH to sys.path
sys.path.append(jasperpath.LIB_PATH)

parser = argparse.ArgumentParser(description='Jasper Voice Control Center')
parser.add_argument('--local', action='store_true',
                    help='Use text input instead of a real microphone')
parser.add_argument('--no-network-check', action='store_true',
                    help='Disable the network connection check')
parser.add_argument('--diagnose', action='store_true',
                    help='Run diagnose and exit')
parser.add_argument('--list-plugins', action='store_true',
                    help='List plugins and exit')
parser.add_argument('--debug', action='store_true', help='Show debug messages')
args = parser.parse_args()

if args.local:
    from client.local_mic import Mic
else:
    from client.mic import Mic


class Jasper(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)

        # Create config dir if it does not exist yet
        if not os.path.exists(jasperpath.CONFIG_PATH):
            try:
                os.makedirs(jasperpath.CONFIG_PATH)
            except OSError:
                self._logger.error("Could not create config dir: '%s'",
                                   jasperpath.CONFIG_PATH, exc_info=True)
                raise

        # Check if config dir is writable
        if not os.access(jasperpath.CONFIG_PATH, os.W_OK):
            self._logger.critical("Config dir %s is not writable. Jasper " +
                                  "won't work correctly.",
                                  jasperpath.CONFIG_PATH)

        # FIXME: For backwards compatibility, move old config file to newly
        #        created config dir
        old_configfile = os.path.join(jasperpath.LIB_PATH, 'profile.yml')
        new_configfile = jasperpath.config('profile.yml')
        if os.path.exists(old_configfile):
            if os.path.exists(new_configfile):
                self._logger.warning("Deprecated profile file found: '%s'. " +
                                     "Please remove it.", old_configfile)
            else:
                self._logger.warning("Deprecated profile file found: '%s'. " +
                                     "Trying to copy it to new location '%s'.",
                                     old_configfile, new_configfile)
                try:
                    shutil.copy2(old_configfile, new_configfile)
                except shutil.Error:
                    self._logger.error("Unable to copy config file. " +
                                       "Please copy it manually.",
                                       exc_info=True)
                    raise

        # Read config
        self._logger.debug("Trying to read config file: '%s'", new_configfile)
        try:
            with open(new_configfile, "r") as f:
                self.config = yaml.safe_load(f)
        except OSError:
            self._logger.error("Can't open config file: '%s'", new_configfile)
            raise

        try:
            stt_engine_slug = self.config['stt_engine']
        except KeyError:
            stt_engine_slug = 'sphinx'
            logger.warning("stt_engine not specified in profile, defaulting " +
                           "to '%s'", stt_engine_slug)
        stt_engine_class = stt.get_engine_by_slug(stt_engine_slug)

        try:
            slug = self.config['stt_passive_engine']
            stt_passive_engine_class = stt.get_engine_by_slug(slug)
        except KeyError:
            stt_passive_engine_class = stt_engine_class

        try:
            tts_engine_slug = self.config['tts_engine']
        except KeyError:
            tts_engine_slug = tts.get_default_engine_slug()
            logger.warning("tts_engine not specified in profile, defaulting " +
                           "to '%s'", tts_engine_slug)
        tts_engine_class = tts.get_engine_by_slug(tts_engine_slug)

        # Initialize AudioEngine
        audio = audioengine.PyAudioEngine()

        # Initialize audio input device
        devices = [device.slug for device
                   in audio.get_input_devices()]
        try:
            device_slug = self.config['input_device']
        except KeyError:
            device_slug = audio.get_default_input_device().slug
            logger.warning("input_device not specified in profile, " +
                           "defaulting to '%s' (Possible values: %s)",
                           device_slug, ', '.join(devices))
        try:
            input_device = audio.get_device_by_slug(device_slug)
            if not input_device.is_input_device:
                raise audioengine.UnsupportedFormat(
                    "Audio device with slug '%s' is not an input device"
                    % input_device.slug)
        except (audioengine.DeviceException) as e:
            logger.critical(e.args[0])
            logger.warning('Valid output devices: %s', ', '.join(devices))
            raise

        # Initialize audio output device
        devices = [device.slug for device
                   in audio.get_output_devices()]
        try:
            device_slug = self.config['output_device']
        except KeyError:
            device_slug = audio.get_default_output_device().slug
            logger.warning("output_device not specified in profile, " +
                           "defaulting to '%s' (Possible values: %s)",
                           device_slug, ', '.join(devices))
        try:
            output_device = audio.get_device_by_slug(device_slug)
            if not output_device.is_output_device:
                raise audioengine.UnsupportedFormat(
                    "Audio device with slug '%s' is not an output device"
                    % output_device.slug)
        except (audioengine.DeviceException) as e:
            logger.critical(e.args[0])
            logger.warning('Valid output devices: %s', ', '.join(devices))
            raise

        # Load plugins
        self.plugins = pluginstore.PluginStore([jasperpath.PLUGIN_PATH])
        self.plugins.detect_plugins()

        # Initialize Brain
        self.brain = brain.Brain()
        for info in self.plugins.get_plugins_by_category('speechhandler'):
            try:
                plugin = info.plugin_class(info, self.config)
            except:
                debug = self._logger.getEffectiveLevel() == logging.DEBUG
                self._logger.warning("Plugin '%s' caused an error!", info.name,
                                     exc_info=debug)
            else:
                self.brain.add_plugin(plugin)

        # Initialize Mic
        self.mic = Mic(
            input_device, output_device,
            stt_passive_engine_class.get_instance(
                'keyword', self.brain.get_keyword_phrases()),
            stt_engine_class.get_instance(
                'default', self.brain.get_all_phrases()),
            tts_engine_class.get_instance())

        self.conversation = Conversation("JASPER", self.mic, self.brain,
                                         self.config)

    def run(self):
        if 'first_name' in self.config:
            salutation = ("How can I be of service, %s?"
                          % self.config["first_name"])
        else:
            salutation = "How can I be of service?"
        self.mic.say(salutation)

        self.conversation.handleForever()

if __name__ == "__main__":

    print("*******************************************************")
    print("*             JASPER - THE TALKING COMPUTER           *")
    print("* (c) 2015 Shubhro Saha, Charlie Marsh & Jan Holthuis *")
    print("*******************************************************")

    logging.basicConfig()
    logger = logging.getLogger()
    logger.getChild("client.stt").setLevel(logging.INFO)

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if not args.no_network_check and not diagnose.check_network_connection():
        logger.warning("Network not connected. This may prevent Jasper from " +
                       "running properly.")

    if args.list_plugins:
        pstore = pluginstore.PluginStore([jasperpath.PLUGIN_PATH])
        pstore.detect_plugins()
        plugins = pstore.get_plugins()
        len_name = max(len(info.name) for info in plugins)
        len_version = max(len(info.version) for info in plugins)
        for info in plugins:
            print("%s %s - %s" % (info.name.ljust(len_name),
                                  ("(v%s)" % info.version).ljust(len_version),
                                  info.description))
        sys.exit(1)

    if args.diagnose:
        failed_checks = diagnose.run()
        sys.exit(0 if not failed_checks else 1)

    try:
        app = Jasper()
    except Exception:
        logger.error("Error occured!", exc_info=True)
        sys.exit(1)

    app.run()
