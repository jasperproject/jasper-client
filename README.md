jasper-client
=============

Client code for the Jasper voice computing platform. Jasper is an open source platform for developing always-on, voice-controlled applications.

Learn more at [jasperproject.github.io](http://jasperproject.github.io/), where we have assembly and installation instructions, as well as extensive documentation. For the relevant disk image, please visit [SourceForge](http://sourceforge.net/projects/jasperproject/).

## Contributing

If you'd like to contribute to Jasper, we've created a Contributing Guide, available [here](https://github.com/jasperproject/jasper-client/blob/master/CONTRIBUTING.md). It outlines the philosophies to preserve, tests to run, and more. If you're looking for potential features to build, we've included some recommendations there as well.

We highly recommend reading through this guide before writing any code. Thanks in advance for any and all work you contribute to Jasper!

## Contact

Jasper was originally created by [Shubhro Saha](http://www.princeton.edu/~saha/) and [Charles Marsh](http://www.princeton.edu/~crmarsh/). Both can be reached by email at [saha@princeton.edu](mailto:saha@princeton.edu) and [crmarsh@princeton.edu](mailto:crmarsh@princeton.edu) respectively.

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
