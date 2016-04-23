# -*- coding: utf-8 -*-
import os
import logging
import imp
import inspect
import sys
if sys.version_info < (3, 0):  # NOQA
    import ConfigParser as configparser
else:  # NOQA
    import configparser

from . import i18n
from . import plugin


MANDATORY_OPTIONS = (
    ('Plugin', 'Name'),
    ('Plugin', 'Version'),
    ('Plugin', 'License')
)

PLUGIN_INFO_FILENAME = "plugin.info"
PLUGIN_TRANSLATIONS_DIRNAME = "locale"


class PluginError(Exception):
    pass


def parse_info_file(infofile_path):
    logger = logging.getLogger(__name__)
    cp = configparser.RawConfigParser()
    cp.read(infofile_path)

    options_missing = False
    for option in MANDATORY_OPTIONS:
        if not cp.has_option(*option):
            options_missing = True
            logger.debug("Plugin info file '%s' missing value '%s'",
                         infofile_path, option)

    if options_missing:
        raise PluginError("Info file is missing values!")

    logger.debug("Plugin info file '%s' parsed successfully!", infofile_path)
    return cp


def parse_plugin_class(module_name, plugin_directory, superclasses):
    mod = imp.load_module(module_name, None, plugin_directory,
                          ("py", "r", imp.PKG_DIRECTORY))

    plugin_classes = inspect.getmembers(
        mod, lambda cls: inspect.isclass(cls) and
        issubclass(cls, tuple(superclasses)))

    if len(plugin_classes) < 1:
        raise PluginError("Plugin class not found!")

    if len(plugin_classes) > 1:
        raise PluginError("Multiple plugin classes found!")

    return plugin_classes[0][1]


def get_module_name(name, version):
    name = ("%s_%s" % (name, version))
    return name.replace('-', '_').replace('.', '_')


class PluginInfo(object):
    def __init__(self, cp, plugin_class, translations, directory):
        self._cp = cp
        self._plugin_class = plugin_class
        self._translations = translations
        self._path = directory

    def _get_optional_info(self, *args):
        try:
            value = self._cp.get(*args)
        except configparser.Error:
            value = ''
        return value

    @property
    def plugin_class(self):
        return self._plugin_class

    @plugin_class.setter
    def plugin_class(self, value):
        if self._plugin_class is not None:
            raise RuntimeError('Changing a plugin class it not allowed!')
        self._plugins_class = value

    @property
    def translations(self):
        return self._translations

    @property
    def name(self):
        return self._cp.get('Plugin', 'Name')

    @property
    def version(self):
        return self._cp.get('Plugin', 'Version')

    @property
    def license(self):
        return self._cp.get('Plugin', 'License')

    @property
    def description(self):
        return self._get_optional_info('Plugin', 'Description')

    @property
    def url(self):
        return self._get_optional_info('Plugin', 'URL')

    @property
    def author_name(self):
        return self._get_optional_info('Author', 'Name')

    @property
    def author_email(self):
        return self._get_optional_info('Author', 'Email')

    @property
    def author_url(self):
        return self._get_optional_info('Author', 'URL')


class PluginStore(object):
    def __init__(self, plugin_dirs):
        self._logger = logging.getLogger(__name__)
        self._plugin_dirs = [os.path.abspath(os.path.expanduser(d))
                             for d in plugin_dirs]
        self._plugins = {}
        self._info_fname = PLUGIN_INFO_FILENAME
        self._translations_dirname = PLUGIN_TRANSLATIONS_DIRNAME
        self._categories_map = {
            'audioengine': plugin.AudioEnginePlugin,
            'speechhandler': plugin.SpeechHandlerPlugin,
            'tts': plugin.TTSPlugin,
            'stt': plugin.STTPlugin
        }

    def detect_plugins(self):
        for plugin_dir in self._plugin_dirs:
            for root, dirs, files in os.walk(plugin_dir, topdown=True):
                for name in files:
                    if name != self._info_fname:
                        continue
                    try:
                        self._logger.debug("Found plugin candidate at: %s",
                                           root)
                        plugin_info = self.parse_plugin(root)
                    except Exception as e:
                        reason = ''
                        if hasattr(e, 'strerror') and e.strerror:
                            reason = e.strerror
                            if hasattr(e, 'errno') and e.errno:
                                reason += ' [Errno %d]' % e.errno
                        elif hasattr(e, 'message'):
                            reason = e.message
                        elif hasattr(e, 'msg'):
                            reason = e.msg
                        if not reason:
                            reason = 'Unknown'
                        self._logger.warning(
                            "Plugin at '%s' skipped! (Reason: %s)",
                            root, reason,
                            exc_info=self._logger.isEnabledFor(logging.DEBUG))
                    else:
                        if plugin_info.name in self._plugins:
                            self._logger.warning("Duplicate plugin: %s",
                                                 plugin_info.name)
                        else:
                            self._plugins[plugin_info.name] = plugin_info
                            self._logger.debug("Found valid plugin: %s %s",
                                               plugin_info.name,
                                               plugin_info.version)

    def parse_plugin(self, plugin_directory):
        infofile_path = os.path.join(plugin_directory, self._info_fname)
        cp = parse_info_file(infofile_path)

        translations_path = os.path.join(plugin_directory,
                                         self._translations_dirname)
        translations = i18n.parse_translations(translations_path)

        module_name = get_module_name(cp.get('Plugin', 'Name'),
                                      cp.get('Plugin', 'Version'))
        plugin_class = parse_plugin_class(module_name,
                                          plugin_directory,
                                          self._categories_map.values())

        return PluginInfo(cp, plugin_class, translations, plugin_directory)

    def get_plugins_by_category(self, category):
        superclass = self._categories_map[category]
        return [info for info in self._plugins.values()
                if issubclass(info.plugin_class, superclass)]

    def get_plugins(self):
        return self._plugins.values()

    def get_plugin(self, name, category=None):
        if category is None:
            plugins = self.get_plugins()
        else:
            plugins = self.get_plugins_by_category(category)
        for plugin_info in plugins:
            if plugin_info.name == name:
                return plugin_info
        raise PluginError("Plugin '%s' not found!" % name)
