jasper-client
=============

[![Build Status](https://travis-ci.org/jasperproject/jasper-client.svg?branch=master)](https://travis-ci.org/jasperproject/jasper-client) [![Coverage Status](https://img.shields.io/coveralls/jasperproject/jasper-client.svg)](https://coveralls.io/r/jasperproject/jasper-client) [![Codacy Badge](https://www.codacy.com/project/badge/3a50e1bc2261419894d76b7e2c1ac694)](https://www.codacy.com/app/jasperproject/jasper-client)

Client code for the Jasper voice computing platform. Jasper is an open source platform for developing always-on, voice-controlled applications.

Learn more at [jasperproject.github.io](http://jasperproject.github.io/), where we have assembly and installation instructions, as well as extensive documentation. For the relevant disk image, please visit [SourceForge](http://sourceforge.net/projects/jasperproject/).

## Contributing

If you'd like to contribute to Jasper, please read through our **[Contributing Guide](CONTRIBUTING.md)**, which outlines the philosophies to preserve, tests to run, and more. We highly recommend reading through this guide before writing any code.

The Contributing Guide also outlines some prospective features and areas that could use love. However, for a more thorough overview of Jasper's direction and goals, check out the **[Product Roadmap](https://github.com/jasperproject/jasper-client/wiki/Roadmap)**.

Thanks in advance for any and all work you contribute to Jasper!

## Support

If you run into an issue or require technical support, please first look through the closed and open **[GitHub Issues](https://github.com/jasperproject/jasper-client/issues)**, as you may find a solution there (or some useful advice, at least).

If you're still having trouble, the next place to look would be the new **[Google Group support forum](https://groups.google.com/forum/#!forum/jasper-support-forum)**. If your problem remains unsolved, feel free to create a post there describing the issue, the steps you've taken to debug it, etc.

## Contact

Jasper's core developers are [Shubhro Saha](http://www.princeton.edu/~saha/), [Charles Marsh](http://www.princeton.edu/~crmarsh/) and [Jan Holthuis](http://homepage.ruhr-uni-bochum.de/Jan.Holthuis/).  All of them can be reached by email at [saha@princeton.edu](mailto:saha@princeton.edu), [crmarsh@princeton.edu](mailto:crmarsh@princeton.edu) and [jan.holthuis@ruhr-uni-bochum.de](mailto:jan.holthuis@ruhr-uni-bochum.de) respectively. However, for technical support and other problems, please go through the channels mentioned above.

For a complete list of code contributors, please see [AUTHORS.md](AUTHORS.md).

## Major Updates
- 2015-01-19: Added a new TTS engine for [Flite (festival-lite)](https://github.com/jasperproject/jasper-client/pull/286) and an experimental STT engine for [Julius ](https://github.com/jasperproject/jasper-client/pull/285)
- 2015-01-07: [Added a new STT engine](https://github.com/jasperproject/jasper-client/pull/229) for Wit.ai
- 2014-11-05: [Added a new TTS engine](https://github.com/jasperproject/jasper-client/pull/229) for MaryTTS
- 2014-10-13: [Brand-new vocabulary compiler](https://github.com/jasperproject/jasper-client/pull/181) that introduces versioning, so that compilation is only performed when needed.
- 2014-09-27: [Improved TTS implementation](https://github.com/jasperproject/jasper-client/pull/155) and new TTS engines for Festival, SVOX Pico and Google TTS.
- 2014-08-09: [Modularized STT implementation](https://github.com/jasperproject/jasper-client/pull/118) with Google Speech API example, thanks to astahlman. Running `populate.py` after updating is highly recommended.
- 2014-07-11: More [platform-independent audio output](https://github.com/jasperproject/jasper-client/pull/100). Thank you, astahlman!
- 2014-05-27: The network setup wizard has been removed because of unreliability. The client code and documentation has been updated, requiring new users to manually configure their `/etc/network/interfaces` file.

## License

*Copyright (c) 2014-2015, Charles Marsh, Shubhro Saha & Jan Holthuis. All rights reserved.*

Jasper is covered by the MIT license, a permissive free software license that lets you do anything you want with the source code, as long as you provide back attribution and ["don't hold \[us\] liable"](http://choosealicense.com). For the full license text see the [LICENSE.md](LICENSE.md) file.

*Note that this licensing only refers to the Jasper client code (i.e.,  the code on GitHub) and not to the disk image itself (i.e., the code on SourceForge).*
