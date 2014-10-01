jasper-client
=============

[![Build Status](https://travis-ci.org/jasperproject/jasper-client.svg?branch=master)](https://travis-ci.org/jasperproject/jasper-client)

Client code for the Jasper voice computing platform. Jasper is an open source platform for developing always-on, voice-controlled applications.

Learn more at [jasperproject.github.io](http://jasperproject.github.io/), where we have assembly and installation instructions, as well as extensive documentation. For the relevant disk image, please visit [SourceForge](http://sourceforge.net/projects/jasperproject/).

## Contributing

If you'd like to contribute to Jasper, please read through our **[Contributing Guide](https://github.com/jasperproject/jasper-client/blob/master/CONTRIBUTING.md)**, which outlines the philosophies to preserve, tests to run, and more. We highly recommend reading through this guide before writing any code.

The Contributing Guide also outlines some prospective features and areas that could use love. However, for a more thorough overview of Jasper's direction and goals, check out the **[Product Roadmap](https://github.com/jasperproject/jasper-client/wiki/Roadmap)**.

Thanks in advance for any and all work you contribute to Jasper!

## Support

If you run into an issue or require technical support, please first look through the closed and open **[GitHub Issues](https://github.com/jasperproject/jasper-client/issues)**, as you may find a solution there (or some useful advice, at least).

If you're still having trouble, the next place to look would be the new **[Google Group support forum](https://groups.google.com/forum/#!forum/jasper-support-forum)**. If your problem remains unsolved, feel free to create a post there describing the issue, the steps you've taken to debug it, etc.

## Contact

Jasper was originally created by [Shubhro Saha](http://www.princeton.edu/~saha/) and [Charles Marsh](http://www.princeton.edu/~crmarsh/). Both can be reached by email at [saha@princeton.edu](mailto:saha@princeton.edu) and [crmarsh@princeton.edu](mailto:crmarsh@princeton.edu) respectively. However, for technical support and other problems, please go through the channels mentioned above.

## Major Updates
- 2014-08-09: [Modularized STT implementation](https://github.com/jasperproject/jasper-client/pull/118) with Google Speech API example, thanks to astahlman. Running `populate.py` after updating is highly recommended.
- 2014-07-11: More [platform-independent audio output](https://github.com/jasperproject/jasper-client/pull/100). Thank you, astahlman!
- 2014-05-27: The network setup wizard has been removed because of unreliability. The client code and documentation has been updated, requiring new users to manually configure their `/etc/network/interfaces` file.

## License

Jasper is released under the MIT license, a permissive free software license that lets you do anything you want with the source code, as long as you provide back attribution and ["don't hold \[us\] liable"](http://choosealicense.com). Note that this licensing only refers to the Jasper client code (i.e.,  the code on GitHub) and not to the disk image itself (i.e., the code on SourceForge).

The MIT License (MIT)

Copyright (c) 2014 Charles Marsh & Shubhro Saha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
