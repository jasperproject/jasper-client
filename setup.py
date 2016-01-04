#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import setuptools

APPNAME = 'jasper'


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
            'data/audio/*.wav',
            'data/locale/*.po',
            'data/standard_phrases/*.txt',
            '../plugins/*/*/*.py',
            '../plugins/*/*/plugin.info',
            '../plugins/*/*/*.txt',
            '../plugins/*/*/locale/*.po',
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
    }
)
