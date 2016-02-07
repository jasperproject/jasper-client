# -*- coding: utf-8 -*-
import logging
import os
import shutil
import yaml
import pkg_resources

from . import audioengine
from . import brain
from . import paths
from . import pluginstore
from . import conversation
from . import mic
from . import local_mic
from . import restapi


class Jasper(object):
    def __init__(self, use_local_mic=False):
        self._logger = logging.getLogger(__name__)

        # Create config dir if it does not exist yet
        if not os.path.exists(paths.CONFIG_PATH):
            try:
                os.makedirs(paths.CONFIG_PATH)
            except OSError:
                self._logger.error("Could not create config dir: '%s'",
                                   paths.CONFIG_PATH, exc_info=True)
                raise

        # Check if config dir is writable
        if not os.access(paths.CONFIG_PATH, os.W_OK):
            self._logger.critical("Config dir %s is not writable. Jasper " +
                                  "won't work correctly.",
                                  paths.CONFIG_PATH)

        # FIXME: For backwards compatibility, move old config file to newly
        #        created config dir
        old_configfile = os.path.join(paths.PKG_PATH, 'profile.yml')
        new_configfile = paths.config('profile.yml')
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
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as e:
            self._logger.error("Unable to parse config file: %s %s",
                               e.problem.strip(), str(e.problem_mark).strip())
            raise

        try:
            language = self.config['language']
        except KeyError:
            self._logger.warning(
                "language not specified in profile, using 'en-US'")
        else:
            self._logger.info("Using language '%s'", language)

        try:
            audio_engine_slug = self.config['audio_engine']
        except KeyError:
            audio_engine_slug = 'pyaudio'
            self._logger.info("audio_engine not specified in profile, using " +
                              "defaults.")
        self._logger.debug("Using Audio engine '%s'", audio_engine_slug)

        try:
            active_stt_slug = self.config['stt_engine']
        except KeyError:
            active_stt_slug = 'sphinx'
            self._logger.warning("stt_engine not specified in profile, " +
                                 "using defaults.")
        self._logger.debug("Using STT engine '%s'", active_stt_slug)

        try:
            passive_stt_slug = self.config['stt_passive_engine']
        except KeyError:
            passive_stt_slug = active_stt_slug
        self._logger.debug("Using passive STT engine '%s'", passive_stt_slug)

        try:
            tts_slug = self.config['tts_engine']
        except KeyError:
            tts_slug = 'espeak-tts'
            self._logger.warning("tts_engine not specified in profile, using" +
                                 "defaults.")
        self._logger.debug("Using TTS engine '%s'", tts_slug)

        try:
            keyword = self.config['keyword']
        except KeyError:
            keyword = 'Jasper'
        self._logger.info("Using keyword '%s'", keyword)

        # Load plugins
        plugin_directories = [
            paths.config('plugins'),
            pkg_resources.resource_filename(__name__, '../plugins')
        ]
        self.plugins = pluginstore.PluginStore(plugin_directories)
        self.plugins.detect_plugins()

        # Initialize AudioEngine
        ae_info = self.plugins.get_plugin(audio_engine_slug,
                                          category='audioengine')
        self.audio = ae_info.plugin_class(ae_info, self.config)

        # Initialize audio input device
        devices = [device.slug for device in self.audio.get_devices(
            device_type=audioengine.DEVICE_TYPE_INPUT)]
        try:
            device_slug = self.config['input_device']
        except KeyError:
            device_slug = self.audio.get_default_device(output=False).slug
            self._logger.warning("input_device not specified in profile, " +
                                 "defaulting to '%s' (Possible values: %s)",
                                 device_slug, ', '.join(devices))
        try:
            input_device = self.audio.get_device_by_slug(device_slug)
            if audioengine.DEVICE_TYPE_INPUT not in input_device.types:
                raise audioengine.UnsupportedFormat(
                    "Audio device with slug '%s' is not an input device"
                    % input_device.slug)
        except (audioengine.DeviceException) as e:
            self._logger.critical(e.args[0])
            self._logger.warning('Valid output devices: %s',
                                 ', '.join(devices))
            raise

        # Initialize audio output device
        devices = [device.slug for device in self.audio.get_devices(
            device_type=audioengine.DEVICE_TYPE_OUTPUT)]
        try:
            device_slug = self.config['output_device']
        except KeyError:
            device_slug = self.audio.get_default_device(output=True).slug
            self._logger.warning("output_device not specified in profile, " +
                                 "defaulting to '%s' (Possible values: %s)",
                                 device_slug, ', '.join(devices))
        try:
            output_device = self.audio.get_device_by_slug(device_slug)
            if audioengine.DEVICE_TYPE_OUTPUT not in output_device.types:
                raise audioengine.UnsupportedFormat(
                    "Audio device with slug '%s' is not an output device"
                    % output_device.slug)
        except (audioengine.DeviceException) as e:
            self._logger.critical(e.args[0])
            self._logger.warning('Valid output devices: %s',
                                 ', '.join(devices))
            raise

        # Initialize Brain
        self.brain = brain.Brain(self.config)
        for info in self.plugins.get_plugins_by_category('speechhandler'):
            try:
                plugin = info.plugin_class(info, self.config)
            except Exception as e:
                self._logger.warning(
                    "Plugin '%s' skipped! (Reason: %s)", info.name,
                    e.message if hasattr(e, 'message') else 'Unknown',
                    exc_info=(
                        self._logger.getEffectiveLevel() == logging.DEBUG))
            else:
                self.brain.add_plugin(plugin)

        if len(self.brain.get_plugins()) == 0:
            msg = 'No plugins for handling speech found!'
            self._logger.error(msg)
            raise RuntimeError(msg)
        elif len(self.brain.get_all_phrases()) == 0:
            msg = 'No command phrases found!'
            self._logger.error(msg)
            raise RuntimeError(msg)

        active_stt_plugin_info = self.plugins.get_plugin(
            active_stt_slug, category='stt')
        active_stt_plugin = active_stt_plugin_info.plugin_class(
            'default', self.brain.get_plugin_phrases(), active_stt_plugin_info,
            self.config)

        if passive_stt_slug != active_stt_slug:
            passive_stt_plugin_info = self.plugins.get_plugin(
                passive_stt_slug, category='stt')
        else:
            passive_stt_plugin_info = active_stt_plugin_info

        passive_stt_plugin = passive_stt_plugin_info.plugin_class(
            'keyword', self.brain.get_standard_phrases() + [keyword],
            passive_stt_plugin_info, self.config)

        tts_plugin_info = self.plugins.get_plugin(tts_slug, category='tts')
        tts_plugin = tts_plugin_info.plugin_class(tts_plugin_info, self.config)

        # Initialize Mic
        if use_local_mic:
            self.mic = local_mic.Mic()
        else:
            self.mic = mic.Mic(
                input_device, output_device,
                passive_stt_plugin, active_stt_plugin,
                tts_plugin, self.config, keyword=keyword)

        self.conversation = conversation.Conversation(
            self.mic, self.brain, self.config)

        # Initialize RESTful API
        self.restapi = restapi.RestAPI(self.config, self.mic,
                                       self.conversation)

    def list_plugins(self):
        plugins = self.plugins.get_plugins()
        len_name = max(len(info.name) for info in plugins)
        len_version = max(len(info.version) for info in plugins)
        for info in plugins:
            print("%s %s - %s" % (info.name.ljust(len_name),
                                  ("(v%s)" % info.version).ljust(len_version),
                                  info.description))

    def list_audio_devices(self):
        for device in self.audio.get_devices():
            device.print_device_info(
                verbose=(self._logger.getEffectiveLevel() == logging.DEBUG))

    def run(self):
        self.conversation.greet()
        self.conversation.handleForever()
