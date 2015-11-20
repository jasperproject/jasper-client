# -*- coding: utf-8 -*-
import logging
import contextlib
import re
import wave
import pyaudio
import slugify

STANDARD_SAMPLE_RATES = (
    8000, 9600, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000, 88200,
    96000, 192000
)


class DeviceException(Exception):
    pass


class UnsupportedFormat(DeviceException):
    pass


class DeviceNotFound(DeviceException):
    pass


class PyAudioEngine(object):
    _PYAUDIO_BIT_MAPPING = {8:  pyaudio.paInt8,
                            16: pyaudio.paInt16,
                            24: pyaudio.paInt24,
                            32: pyaudio.paInt32}

    @classmethod
    def _pyaudio_fmt(cls, bits):
        if bits in cls._PYAUDIO_BIT_MAPPING.keys():
            return cls._PYAUDIO_BIT_MAPPING[bits]

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._pyaudio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio engine finished")

    def __del__(self):
        self._pyaudio.terminate()

    def get_devices(self):
        num_devices = self._pyaudio.get_device_count()
        self._logger.debug('Found %d PyAudio devices', num_devices)
        return [PyAudioDevice(self, self._pyaudio.get_device_info_by_index(i))
                for i in range(num_devices)]

    def get_default_input_device(self):
        try:
            info = self._pyaudio.get_default_input_device_info()
        except IOError:
            devices = self.get_input_devices()
            if len(devices) == 0:
                self._logger.warning('No input devices available!')
                raise DeviceNotFound('No input devices available!')
            try:
                device = [d for d in devices if d.slug == 'default'][0]
            except IndexError:
                device = devices[0]
            return device
        else:
            return PyAudioDevice(self, info)

    def get_default_output_device(self):
        try:
            info = self._pyaudio.get_default_output_device_info()
        except IOError:
            devices = self.get_output_devices()
            if len(devices) == 0:
                self._logger.warning('No input devices available!')
                raise DeviceNotFound('No input devices available!')
            try:
                device = [d for d in devices if d.slug == 'default'][0]
            except IndexError:
                device = devices[0]
            return device
        else:
            return PyAudioDevice(self, info)

    def get_input_devices(self):
        return [device for device in self.get_devices()
                if device.is_input_device]

    def get_output_devices(self):
        return [device for device in self.get_devices()
                if device.is_output_device]

    def get_device_by_slug(self, slug):
        for device in self. get_devices():
            if device.slug == slug:
                return device
        raise DeviceNotFound("Audio device with slug '%s' not found" % slug)


class PyAudioDevice(object):
    RE_PRESLUG = re.compile(r'\(hw:\d,\d\)')

    def __init__(self, engine, info):
        self._logger = logging.getLogger(__name__)
        self._engine = engine
        self._index = info['index']
        self._name = info['name']
        self._max_output_channels = info['maxOutputChannels']
        self._max_input_channels = info['maxInputChannels']
        # slugify the name
        preslug_name = self.RE_PRESLUG.sub('', info['name'])
        if preslug_name.endswith(': - '):
            preslug_name = info['name']
        self._slug = slugify.slugify(preslug_name)

    @property
    def name(self):
        return self._name

    @property
    def slug(self):
        return self._slug

    @property
    def index(self):
        return self._index

    @property
    def is_output_device(self):
        return self._max_output_channels > 0

    @property
    def is_input_device(self):
        return self._max_input_channels > 0

    def supports_format(self, bits, channels, rate, output=True):
        if output:
            direction = 'output'
            if not self.is_output_device:
                return False
        else:
            direction = 'input'
            if not self.is_input_device:
                return False
        sample_fmt = self._engine._pyaudio_fmt(bits)
        if not sample_fmt:
            return False
        direction = 'output' if output else 'input'
        fmt_info = {
            ('%s_device' % direction): self.index,
            ('%s_format' % direction): sample_fmt,
            ('%s_channels' % direction): channels,
            'rate': rate
        }
        try:
            supported = self._engine._pyaudio.is_format_supported(**fmt_info)
        except ValueError as e:
            if e.args in (('Sample format not supported', -9994),
                          ('Invalid sample rate', -9997),
                          ('Invalid number of channels', -9998)):
                return False
            else:
                raise
        else:
            return supported

    @contextlib.contextmanager
    def _open_stream(self, bits, channels, rate, output=True):
        # Check if format is supported
        is_supported_fmt = self.supports_format(bits, channels, rate,
                                                output=output)
        if not is_supported_fmt:
            msg_fmt = ("PyAudioDevice {index} ({name}) doesn't support " +
                       "%s format (Int{bits}, {channels}-channel at" +
                       " {rate} Hz)") % ('output' if output else 'input')
            msg = msg_fmt.format(index=self.index,
                                 name=self.name,
                                 bits=bits,
                                 channels=channels,
                                 rate=rate)
            self._logger.critical(msg)
            raise UnsupportedFormat(msg)
        # Everything looks fine, open the stream
        direction = ('output' if output else 'input')
        stream_kwargs = {
            'format': self._engine._pyaudio_fmt(bits),
            'channels': channels,
            'rate': rate,
            'output': output,
            'input': not output,
            ('%s_device_index' % direction): self.index,
            'frames_per_buffer': 1024 if output else 8192
        }
        stream = self._engine._pyaudio.open(**stream_kwargs)
        self._logger.debug("%s stream opened on device '%s' (%d Hz, %d " +
                           "channel, %d bit)", "output" if output else "input",
                           self.slug, rate, channels, bits)
        try:
            yield stream
        finally:
            stream.close()
            self._logger.debug("%s stream closed on device '%s'",
                               "output" if output else "input", self.slug)

    def record(self, chunksize, *args):
        with self._open_stream(*args, output=False) as stream:
            while True:
                frame = stream.read(chunksize)
                yield frame

    def play_fp(self, fp):
        w = wave.open(fp, 'rb')
        channels = w.getnchannels()
        bits = w.getsampwidth()*8
        rate = w.getframerate()
        with self._open_stream(bits, channels, rate) as stream:
            stream.write(w.readframes(w.getnframes()))
        w.close()

    def play_file(self, filename):
        with open(filename, 'rb') as f:
            self.play_fp(f)

    def print_device_info(self, verbose=False):
        print('[Audio device \'%s\']' % self.slug)
        print('  ID: %d' % self.index)
        print('  Name: %s' % self.name)
        print('  Input device: %s' % ('Yes' if self.is_input_device
                                      else 'No'))
        print('  Output device: %s' % ('Yes' if self.is_output_device
                                       else 'No'))
        if verbose:
            for direction in ('input', 'output'):
                valid = (self.is_output_device
                         if direction == 'output'
                         else self.is_input_device)
                if valid:
                    print('  Supported %s formats:' % direction)
                    formats = []
                    for bits in (8, 16, 24, 32):
                        for channels in (1, 2):
                            for rate in STANDARD_SAMPLE_RATES:
                                args = (bits, channels, rate)
                                if self.supports_format(
                                        *args, output=(direction == 'output')):
                                    formats.append(args)
                    if len(formats) == 0:
                        print('    None')
                    else:
                        n = 4
                        for chunk in (formats[i:i+n]
                                      for i in range(0, len(formats), n)):
                            print('    %s' % ', '.join(
                                "(%d Bit %d CH @ %d Hz)" % fmt
                                for fmt in chunk))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    audioengine = PyAudioEngine()
    devices = audioengine.get_devices()
    for device in devices:
        device.print_device_info(verbose=True)
