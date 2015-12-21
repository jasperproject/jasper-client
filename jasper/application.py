# -*- coding: utf-8 -*-
import logging
import pkg_resources

from . import audioengine
from . import brain
from . import config
from . import paths
from . import pluginstore
from . import conversation
from . import mic
from . import local_mic


class Jasper(object):
    def __init__(self, use_local_mic=False):
        self._logger = logging.getLogger(__name__)

        self.config = config.Configuration([paths.config('profile.cfg')])
        self.config.read_defaults([paths.data('defaults.cfg')])

        language = self.config.get('language')
        if not language:
            self._logger.warning(
                "language not specified in profile, using 'en-US'")
        else:
            self._logger.info("Using language '%s'", language)

        audio_engine_slug = self.config.get('audio_engine')
        if not audio_engine_slug:
            audio_engine_slug = 'pyaudio'
            self._logger.info("audio_engine not specified in profile, using " +
                              "defaults.")
        self._logger.debug("Using Audio engine '%s'", audio_engine_slug)

        active_stt_slug = self.config.get('stt_engine')
        if not active_stt_slug:
            active_stt_slug = 'sphinx'
            self._logger.warning("stt_engine not specified in profile, " +
                                 "using defaults.")
        self._logger.debug("Using STT engine '%s'", active_stt_slug)

        passive_stt_slug = self.config.get('stt_passive_engine')
        if not passive_stt_slug:
            passive_stt_slug = active_stt_slug
        self._logger.debug("Using passive STT engine '%s'", passive_stt_slug)

        tts_slug = self.config.get('tts_engine')
        if not tts_slug:
            tts_slug = 'espeak-tts'
            self._logger.warning("tts_engine not specified in profile, using" +
                                 "defaults.")
        self._logger.debug("Using TTS engine '%s'", tts_slug)

        keyword = self.config.get('keyword')
        if not keyword:
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
        device_slug = self.config.get('input_device')
        if not device_slug:
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
        device_slug = self.config.get('output_device')
        if not device_slug:
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
