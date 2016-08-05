import gettext
import os.path
import re

RE_TRANSLATIONS = re.compile(r'^[a-z]{2}(-[A-Z]{2}){0,1}$')


def parse_translations(translations_path):
    translations = {}
    if os.path.isdir(translations_path):
        for content in os.listdir(translations_path):
            if not os.path.isdir(os.path.join(translations_path, content)):
                lang, ext = os.path.splitext(content)
                if ext == (os.extsep + 'mo') and RE_TRANSLATIONS.match(lang):
                    with open(os.path.join(translations_path, content),
                              mode="rb") as f:
                        translations[lang] = gettext.GNUTranslations(f)
    if not translations:
        # Untranslated module, assume hardcoded en-US strings
        translations['en-US'] = gettext.NullTranslations()
    return translations


class GettextMixin(object):
    def __init__(self, translations, config):
        self.__config = config
        self.__translations = translations
        self.__get_translations()

    def __get_translations(self):
        try:
            language = self.__config['language']
        except KeyError:
            language = 'en-US'

        if language not in self.__translations:
            raise ValueError('Unsupported Language!')

        return self.__translations[language]

    def gettext(self, *args, **kwargs):
        return self.__get_translations().gettext(*args, **kwargs).decode(
            'utf-8')

    def ngettext(self, *args, **kwargs):
        return self.__get_translations().ngettext(*args, **kwargs)
