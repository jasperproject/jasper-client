jasper-client - Snowboy Hot Word Detection
=============

[![Build Status](https://travis-ci.org/jasperproject/jasper-client.svg?branch=master)](https://travis-ci.org/jasperproject/jasper-client) [![Coverage Status](https://img.shields.io/coveralls/jasperproject/jasper-client.svg)](https://coveralls.io/r/jasperproject/jasper-client) [![Codacy Badge](https://www.codacy.com/project/badge/3a50e1bc2261419894d76b7e2c1ac694)](https://www.codacy.com/app/jasperproject/jasper-client)

Client code for the Jasper voice computing platform. Jasper is an open source platform for developing always-on, voice-controlled applications.

Learn more at [jasperproject.github.io](http://jasperproject.github.io/), where we have assembly and installation instructions, as well as extensive documentation. For the relevant disk image, please visit [SourceForge](http://sourceforge.net/projects/jasperproject/).

## The differences with the main project

The problem with stt online, it's the big lack of PriVAcy !!!

In jasper by adding stt_passive_engine in profile.yml you can choose the stt who gonna listen to you til you said "Jasper !".
Of course you have to choose a not online stt, if you mind about your PriVAcy...

That's good But !
- You can't easily choose a wake up word.
- Due to my accent (I think),  when i said "Jasper"... doesn't work all the time...

To address these points, i decide to use "Snowboy Hot Word Detection" [https://snowboy.kitt.ai/](https://snowboy.kitt.ai/) as "stt passive engine".
- Define and train your own hotword
- High accuracy, 
- Low latency and no internet needed
- Small memory footprint and cross-platform support

## Installation

- Follow the python installation -> [https://github.com/Kitt-AI/snowboy](https://github.com/Kitt-AI/snowboy)
- copy _snowboydetect.so (generated in project snowboy/swig/Python) in jasper/client/snowboy
- create your model -> [https://snowboy.kitt.ai/](https://snowboy.kitt.ai/)
- copy your model under the name "model.pmdl" in /jasper/client/snowboy)
- And here we go !!!

## TODO

- Remove "Persona" in the code
- Remove all the dependance in the code stt_passive_engine
- Too much latence in active listenning.
- Re add gmail notification 

## Contributing

If you'd like to contribute to Jasper, please read through our **[Contributing Guide](CONTRIBUTING.md)**, which outlines the philosophies to preserve, tests to run, and more. We highly recommend reading through this guide before writing any code.

The Contributing Guide also outlines some prospective features and areas that could use love. However, for a more thorough overview of Jasper's direction and goals, check out the **[Product Roadmap](https://github.com/jasperproject/jasper-client/wiki/Roadmap)**.

Thanks in advance for any and all work you contribute to Jasper!

## Support

If you run into an issue or require technical support, please first look through the closed and open **[GitHub Issues](https://github.com/jasperproject/jasper-client/issues)**, as you may find a solution there (or some useful advice, at least).

If you're still having trouble, the next place to look would be the new **[Google Group support forum](https://groups.google.com/forum/#!forum/jasper-support-forum)**. If your problem remains unsolved, feel free to create a post there describing the issue, the steps you've taken to debug it, etc.

## Contact

Jasper's core developers are [Shubhro Saha](http://www.shubhro.com), [Charles Marsh](http://www.crmarsh.com) and [Jan Holthuis](http://homepage.ruhr-uni-bochum.de/Jan.Holthuis/).  All of them can be reached by email at [saha@princeton.edu](mailto:saha@princeton.edu), [crmarsh@princeton.edu](mailto:crmarsh@princeton.edu) and [jan.holthuis@ruhr-uni-bochum.de](mailto:jan.holthuis@ruhr-uni-bochum.de) respectively. However, for technical support and other problems, please go through the channels mentioned above.

For a complete list of code contributors, please see [AUTHORS.md](AUTHORS.md).

## License

*Copyright (c) 2014-2015, Charles Marsh, Shubhro Saha & Jan Holthuis. All rights reserved.*

Jasper is covered by the MIT license, a permissive free software license that lets you do anything you want with the source code, as long as you provide back attribution and ["don't hold \[us\] liable"](http://choosealicense.com). For the full license text see the [LICENSE.md](LICENSE.md) file.

*Note that this licensing only refers to the Jasper client code (i.e.,  the code on GitHub) and not to the disk image itself (i.e., the code on SourceForge).*
