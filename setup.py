#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import msgfmt
import setuptools
from setuptools.command.bdist_egg import bdist_egg
from distutils.command.build import build

APPNAME = 'jasper'


class jasper_bdist_egg(bdist_egg):
    def run(self):
        self.run_command('build_i18n')
        setuptools.command.bdist_egg.bdist_egg.run(self)


class jasper_build_i18n(setuptools.Command):
    description = 'compile PO translations to MO files'

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for root, _, filenames in os.walk(os.path.dirname(__file__)):
            for po_filename in filenames:
                filename, ext = os.path.splitext(po_filename)
                if ext != '.po':
                    continue
                path = os.path.join(root, filename)
                po_path = os.extsep.join([path, 'po'])
                mo_path = os.extsep.join([path, 'mo'])
                print('compile %s -> %s' % (po_path, mo_path))
                with open(mo_path, 'wb') as f:
                    f.write(msgfmt.Msgfmt(po_path).get())


class jasper_build(build):
    sub_commands = build.sub_commands + [
        ('build_i18n', None)
    ]


setuptools.setup(
    name=APPNAME,
    version='2.0a1.dev1',
    url='http://jasperproject.github.io/',
    license='MIT',

    author='Shubhro Saha, Charlie Marsh, Jan Holthuis',
    author_email=(
        'saha@princeton.edu, ' +
        'crmarsh@princeton.edu, ' +
        'jan.holthuis@ruhr-uni-bochum.de'
    ),

    description=(
        'Jasper is an open source platform for developing ' +
        'always-on, voice-controlled applications.'
    ),

    install_requires=[
        'APScheduler',
        'argparse',
        'mock',
        'python-slugify',
        'pytz',
        'PyYAML',
        'requests'
    ],

    packages=[APPNAME],
    package_data={
        APPNAME: [
            'data/defaults.cfg',
            'data/audio/*.wav',
            'data/locale/*.po',
            'data/locale/*.mo',
            'data/standard_phrases/*.txt',
            '../plugins/*/*/*.py',
            '../plugins/*/*/plugin.info',
            '../plugins/*/*/*.txt',
            '../plugins/*/*/locale/*.po',
            '../plugins/*/*/locale/*.mo',
            '../plugins/*/*/tests/*.py'
        ]
    },

    data_files=[
        ('share/doc/%s' % APPNAME, [
            'AUTHORS.md',
            'CONTRIBUTING.md',
            'LICENSE.md',
            'README.md'
        ])
    ],

    entry_points={
        'console_scripts': [
            'Jasper = %s.main:main' % APPNAME
        ]
    },

    cmdclass={
        'bdist_egg': jasper_bdist_egg,
        'build': jasper_build,
        'build_i18n': jasper_build_i18n,
    },

    test_suite='tests'
)
