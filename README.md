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

Additionally, you are expected to have:

- a **Speaker** to plug into Raspberry Pi's headphone jack
- a **USB Microphone**
