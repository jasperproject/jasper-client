#jasper-client

Client code for the Jasper voice computing platform. Jasper is an open source platform for developing always-on, voice-controlled applications.

Learn more at [jasperproject.github.io](http://jasperproject.github.io/), where we have assembly and installation instructions, as well as extensive documentation.

### Obtaining an API Key
This version of Jasper has been configured to use Google's Speech To Text (STT) API. Due to recent changes of the API, all users must have an API key in order for Jasper to function fully. Following these steps should give you access within minutes.

1. Go to [Google's Developer Console](https://cloud.google.com/console) and create a new project.
2. Join the [Chromium Developer Group](https://groups.google.com/a/chromium.org/forum/?fromgroups#!forum/chromium-dev)
3. In the Developer Console, select your new project > "APIs & Auth" > activate "Speech API"
4. Under "APIs & Auth", go to "Credentials" and create a client
5. Next, select "Create New Key" (both Browser and Server keys have been tested to work)
6. Copy the Key for later.

You will be prompted for your key when running populate.py upon installation.

## Additional Installations
### Required Installations
```
sudo pip install --upgrade setuptools
``` 
```
sudo pip install -r jasper/client/requirements.txt
```
##### Raspberry Pi Users
Raspberry Pi users must configure their ```/etc/asound.conf``` file. More help can be found [here](http://atgn.tumblr.com/post/54588497569/how-to-set-default-audio-input-output-devices-on). For example:
```
pcm.!default {
type hw
card 1
}

ctl.!default {
type hw
card 1
}
```

### Optional Installations
```sudo pip install ouimeaux``` <== This is for control of WeMo switches

## Contact

Jasper is developed by [Shubhro Saha](http://www.princeton.edu/~saha/) and [Charles Marsh](http://www.princeton.edu/~crmarsh/). Both can be reached by email at [saha@princeton.edu](mailto:saha@princeton.edu) and [crmarsh@princeton.edu](mailto:crmarsh@princeton.edu) respectively.

## Contributions

Jasper has recieved contributions by:
- [FRITZ|FRITZ](http://www.fritztech.net) ( [fritz@fritztech.net](mailto:fritz@fritztech.net) )
- [Exadrid](https://github.com/Exadrid)

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
