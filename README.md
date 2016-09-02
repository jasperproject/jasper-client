# Judy - Simplified Voice Control on Raspberry Pi

Judy is a simplified sister of [Jasper](http://jasperproject.github.io/),
with a focus on education. It is designed to run on:

**Raspberry Pi 3**  
**Raspbian Jessie**  
**Python 2.7**  

Unlike Jasper, Judy does *not* try to be cross-platform, does *not* allow you to
pick your favorite Speech-to-Text engine or Text-to-Speech engine, does *not*
come with an API for pluggable modules. Judy tries to keep things simple, lets
you experience the joy of voice control with as little hassle as possible.

A **Speech-to-Text engine** is a piece of software that interprets human voice into
a string of text. It lets the computer know what is being said. Conversely,
a **Text-to-Speech engine** converts text into sound. It allows the computer to
speak, probably as a response to your command.

Judy uses:

- **[Pocketsphinx](http://cmusphinx.sourceforge.net/)** as the Speech-to-Text engine
- **[Pico](https://github.com/DougGore/picopi)** as the Text-to-Speech engine

Additionally, you need:

- a **Speaker** to plug into Raspberry Pi's headphone jack
- a **USB Microphone**

**Plug them in.** Let's go.

## Know the Sound Cards

```
$ more /proc/asound/cards
 0 [ALSA           ]: bcm2835 - bcm2835 ALSA
                      bcm2835 ALSA
 1 [Device         ]: USB-Audio - USB PnP Audio Device
                      USB PnP Audio Device at usb-3f980000.usb-1.4, full speed
```

The first is Raspberry Pi's built-in sound card. It has an index of 0. (Note
the word `ALSA`. It means *Advanced Linux Sound Architecture*. Simply put, it
is the sound driver on many Linux systems.)

The second is the USB device's sound card. It has an index of 1.

Your settings might be different. But if you are using Pi 3 with Jessie and have
not changed any sound settings, the above situation is likely to match yours.
For the rest of discussions, I am going to assume:

- Build-in sound card, index **0** → headphone jack → speaker
- USB sound card, index **1** → microphone

The index is important. It is how you tell Raspberry Pi where to get sound data
from, or where to dump sound data into.

If your sound card indexes are different from mine, adjust command arguments
accordingly in what follows.

## Record a WAV file

```
$ arecord -D plughw:1,0 abc.wav
```

## Play a WAV file

```
$ aplay -D plughw:0,0 abc.wav
```

## Install Pico

```
$ sudo apt-get install libttspico-utils
$ pico2wave -w abc.wav "Good morning. How are you today?"
$ aplay -D plughw:0,0 abc.wav
```

## Install Pocketsphinx

```
$ sudo apt-get install pocketsphinx
$ pocketsphinx_continuous -adcdev plughw:1,0 -inmic yes
```

## Configure Pocketsphinx

Comming soon ...

## Install Judy

```
$ sudo pip install jasper-judy
```

More to come ...
