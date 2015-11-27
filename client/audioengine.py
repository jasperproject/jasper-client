# -*- coding: utf-8 -*-
import abc
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

DEVICE_TYPE_ALL = 'all'
DEVICE_TYPE_INPUT = 'input'
DEVICE_TYPE_OUTPUT = 'output'


class DeviceException(Exception):
    pass


class UnsupportedFormat(DeviceException):
    pass


class DeviceNotFound(DeviceException):
    pass


class AudioEngine(object):
    @abc.abstractmethod
    def get_devices(self, device_type=DEVICE_TYPE_ALL):
        pass

    @abc.abstractmethod
    def get_default_device(self, output=True):
        pass

    @abc.abstractmethod
    def get_device_by_slug(self, slug):
        pass


class AudioDevice(object):
    def __init__(self, name):
        self._name = name
        self._slug = slugify.slugify(name)

    @property
    def name(self):
        return self._name

    @property
    def slug(self):
        return self._slug

    @abc.abstractproperty
    def types(self):
        pass

    @abc.abstractmethod
    def supports_format(self, bits, channels, rate, output=True):
        pass

    @abc.abstractmethod
    @contextlib.contextmanager
    def open_stream(self, bits, channels, rate, chunksize=1024, output=True):
        pass

    @abc.abstractmethod
    def record(self, chunksize, *args):
        with self.open_stream(*args, chunksize=chunksize,
                              output=False) as stream:
            while True:
                try:
                    frame = stream.read(chunksize)
                except IOError as e:
                    if type(e.errno) is not int:
                        # Simple hack to work around the fact that the
                        # errno/strerror arguments were swapped in older
                        # PyAudio versions. This was fixed in upstream
                        # commit 1783aaf9bcc6f8bffc478cb5120ccb6f5091b3fb.
                        strerror, errno = e.errno, e.strerror
                    else:
                        strerror, errno = e.strerror, e.errno
                    self._logger.warning("IO error while reading from device" +
                                         " '%s': '%s' (Errno: %d)", self.slug,
                                         strerror, errno)
                else:
                    yield frame

    def play_fp(self, fp):
        w = wave.open(fp, 'rb')
        channels = w.getnchannels()
        bits = w.getsampwidth()*8
        rate = w.getframerate()
        chunksize = 1024
        with self.open_stream(bits, channels, rate,
                              chunksize=chunksize) as stream:
            data = w.readframes(chunksize)
            while data:
                stream.write(data)
                data = w.readframes(chunksize)
        w.close()

    def play_file(self, filename):
        with open(filename, 'rb') as f:
            self.play_fp(f)

    def print_device_info(self, verbose=False):
        print('[Audio device \'%s\']' % self.slug)
        print('  Name: %s' % self.name)
        print('  Input device: %s' % ('Yes'
                                      if DEVICE_TYPE_INPUT in self.types
                                      else 'No'))
        print('  Output device: %s' % ('Yes'
                                       if DEVICE_TYPE_OUTPUT in self.types
                                       else 'No'))
        if verbose:
            for io_type in self.types:
                direction = 'output' if DEVICE_TYPE_OUTPUT else 'input'
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


class PyAudioEngine(AudioEngine):
    _PYAUDIO_BIT_MAPPING = {8:  pyaudio.paInt8,
                            16: pyaudio.paInt16,
                            24: pyaudio.paInt24,
                            32: pyaudio.paInt32}

    @classmethod
    def _pyaudio_fmt(cls, bits):
        if bits in cls._PYAUDIO_BIT_MAPPING.keys():
            return cls._PYAUDIO_BIT_MAPPING[bits]

    def __init__(self):
        super(PyAudioEngine, self).__init__()
        self._logger = logging.getLogger(__name__)
        self._logger.info("Initializing PyAudio. ALSA/Jack error messages " +
                          "that pop up during this process are normal and " +
                          "can usually be safely ignored.")
        self._pyaudio = pyaudio.PyAudio()
        self._logger.info("Initialization of PyAudio engine finished")

    def __del__(self):
        self._pyaudio.terminate()

    def get_devices(self, device_type=DEVICE_TYPE_ALL):
        num_devices = self._pyaudio.get_device_count()
        self._logger.debug('Found %d PyAudio devices', num_devices)
        devs = [PyAudioDevice(self, self._pyaudio.get_device_info_by_index(i))
                for i in range(num_devices)]
        if device_type == DEVICE_TYPE_ALL:
            return devs
        else:
            return [device for device in devs if device_type in device.types]

    def get_default_device(self, output=True):
        try:
            if output:
                info = self._pyaudio.get_default_output_device_info()
            else:
                info = self._pyaudio.get_default_input_device_info()
        except IOError:
            direction = 'output' if output else 'input'
            devices = self.get_devices(device_type=(
                DEVICE_TYPE_OUTPUT if output else DEVICE_TYPE_INPUT))
            if len(devices) == 0:
                msg = 'No %s devices available!' % direction
                self._logger.warning(msg)
                raise DeviceNotFound(msg)
            try:
                device = [d for d in devices if d.slug == 'default'][0]
            except IndexError:
                device = devices[0]
            return device
        else:
            return PyAudioDevice(self, info)

    def get_device_by_slug(self, slug):
        for device in self. get_devices():
            if device.slug == slug:
                return device
        raise DeviceNotFound("Audio device with slug '%s' not found" % slug)


class PyAudioDevice(AudioDevice):
    RE_PRESLUG = re.compile(r'\(hw:\d,\d\)')

    def __init__(self, engine, info):
        super(PyAudioDevice, self).__init__(info['name'])
        self._logger = logging.getLogger(__name__)
        self._engine = engine
        self._index = info['index']
        self._max_output_channels = info['maxOutputChannels']
        self._max_input_channels = info['maxInputChannels']
        # slugify the name
        preslug_name = self.RE_PRESLUG.sub('', self.name)
        if preslug_name.endswith(': - '):
            preslug_name = self.name
        self._pyaudio_slug = slugify.slugify(preslug_name)

    @property
    def slug(self):
        return self._pyaudio_slug

    @property
    def index(self):
        return self._index

    @property
    def types(self):
        types = []
        if self._max_input_channels > 0:
            types.append(DEVICE_TYPE_INPUT)
        if self._max_output_channels > 0:
            types.append(DEVICE_TYPE_OUTPUT)
        return tuple(types)

    def supports_format(self, bits, channels, rate, output=True):
        req_dev_type = DEVICE_TYPE_OUTPUT if output else DEVICE_TYPE_INPUT
        if req_dev_type not in self.types:
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
    def open_stream(self, bits, channels, rate, chunksize=1024, output=True):
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
            'frames_per_buffer': chunksize if output else chunksize*8  # Hacky
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
        with self.open_stream(*args, chunksize=chunksize,
                              output=False) as stream:
            while True:
                try:
                    frame = stream.read(chunksize)
                except IOError as e:
                    if type(e.errno) is not int:
                        # Simple hack to work around the fact that the
                        # errno/strerror arguments were swapped in older
                        # PyAudio versions. This was fixed in upstream
                        # commit 1783aaf9bcc6f8bffc478cb5120ccb6f5091b3fb.
                        strerror, errno = e.errno, e.strerror
                    else:
                        strerror, errno = e.strerror, e.errno
                    self._logger.warning("IO error while reading from device" +
                                         " '%s': '%s' (Errno: %d)", self.slug,
                                         strerror, errno)
                else:
                    yield frame
