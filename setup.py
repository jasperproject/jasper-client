from setuptools import setup

setup(
    name='jasper-judy',
    py_modules = ['judy'],

    version='0.1',

    description='Simplified Voice Control on Raspberry Pi',

    long_description='',

    # The project's main homepage.
    url='https://github.com/nickoala/judy',

    # Author details
    author='Nick Lee',
    author_email='lee1nick@yahoo.ca',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Education',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    # What does your project relate to?
    keywords='speech recognition voice control raspberry pi',
)
