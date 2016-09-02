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

- Build-in sound card, **index 0** → headphone jack → speaker
- USB sound card, **index 1** → microphone

The index is important. It is how you tell Raspberry Pi where to get sound data
from, or where to dump sound data into.

*If your sound card indexes are different from mine, adjust command arguments
accordingly in the rest of this page.*

## Record a WAV file

Enter this command, then speak to the mic, press `Ctrl-C` when you are
finished:

```
$ arecord -D plughw:1,0 abc.wav
```

`-D plughw:1,0` tells `arecord` where the device is. In this case, device is
the mic. It is at index 1.

`plughw:1,0` actually refers to "Sound Card index 1, Subdevice 0", because a
sound card may house many subdevices. Here, we don't care about subdevices and
always give it a `0`. The only important index is the sound card's.

## Play a WAV file

```
$ aplay -D plughw:0,0 abc.wav
```

Here, we tell `aplay` to play to `plughw:0,0`, which refers to "Sound Card index 0,
Subdevice 0", which leads to the speaker.

If you hear nothing, check the speaker's power. After that, try adjusting the
speaker volume with:

```
$ alsamixer
```

On PuTTY, the function keys (`F1`, `F2`, etc) may not behave as expected. If so,
you need to change PuTTY settings:

1. Go to **Terminal** / **Keyboard**
2. Look for section **The Function keys and keypad**
3. Select **Xterm R6**
4. Press button **Apply**

## Install Pico, the Text-to-Speech engine

```
$ sudo apt-get install libttspico-utils
$ pico2wave -w abc.wav "Good morning. How are you today?"
$ aplay -D plughw:0,0 abc.wav
```

## Install Pocketsphinx, the Speech-to-Text engine

```
$ sudo apt-get install pocketsphinx
$ pocketsphinx_continuous -adcdev plughw:1,0 -inmic yes
```

`pocketsphinx_continuous` interprets speech in *real-time*. It will spill out
a lot of stuff, ending with something like this:

```
Warning: Could not find Capture element
READY....
```

Now, **speak into the mic**, and note the results. At first, you may find it
funny. After a while, you realize it is inaccurate.

For it to be useful, we have to make it more accurate.

## Configure Pocketsphinx

We can make it more accurate by restricting its vocabulary. Think of a bunch of
phrases or words you want it to recognize, and save them in a text file.
For example:
```
How are you today
Good morning
night
afternoon
```

Go to Carnegie Mellon University's [lmtool page](http://www.speech.cs.cmu.edu/tools/lmtool-new.html),
upload the text file, and compile the "knowledge base". The "knowledge base" is
nothing more than a bunch of files combined into a zip file. Download and unzip
it:

```
$ wget <URL of the TAR????.tgz FILE>
$ tar zxf <TAR????.tgz>
```

Among the unzipped products, there is a `.lm` and `.dic` file. They basically
define a vocabulary. Pocketsphinx cannot know any words outside of this book.
Supply them to `pocketsphinx_continuous`:

```
$ pocketsphinx_continuous -adcdev plughw:1,0 -lm </path/to/1234.lm> -dic </path/to/1234.dic> -inmic yes
```

Speak into the mic again, but *only those words you have given*. A much better
accuracy should be achieved. Pocketsphinx finally knows what you are talking
about.

## Install Judy

```
$ sudo pip install jasper-judy
```

Judy brings Pocketsphinx's listening ability and Pico's speaking ability
together. A Judy program, on hearing her name being called, can verbally answer
your voice command. Imagine the following sequence:

You: Judy!  
*Judy: [high beep]*  
You: Weather next Monday?  
*Judy: [low beep]*  
*Judy: 23 degrees, partly cloudy*  

She can be as smart as you program her to be.

To get a Judy program running, you need to prepare a few *resources*:

- a `.lm` and `.dic` file to increase listening accuracy
- a folder in which the [beep] audio files reside

[Here are some sample resources.](https://github.com/nickoala/judy/tree/master/resources)
Download them if you want.

A Judy program follows these steps:

1. Create a `VoiceIn` object. Supply it with the microphone device,
and the `.lm` and `.dic` file.
2. Create a `VoiceOut` object. Supply it with the speaker device, and the folder
in which the [beep] audio files reside.
3. Define a function to handle voice commands.
4. Call the function `listen()`.

Here is an example that **echoes whatever you say**. Remember, you have to call
"Judy" to get her attention. After a high beep, you can say something (stay
within the vocabulary, please). A low beep indicates she heard you.
Then, she echoes what you have said.

```python
import judy

vin = judy.VoiceIn(adcdev='plughw:1,0',
                   lm='/home/pi/judy/resources/lm/0931.lm',
                   dict='/home/pi/judy/resources/lm/0931.dic')

vout = judy.VoiceOut(device='plughw:0,0',
                     resources='/home/pi/judy/resources/audio')

def handle(phrase):
    print 'Heard:', phrase
    vout.say(phrase)

judy.listen(vin, vout, handle)
```

It's that simple! Put more stuff in the `handle()` function to make it as smart
as you want her to be.
