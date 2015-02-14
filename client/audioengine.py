# -*- coding: utf-8-*-
import logging
import contextlib
import re
import wave
import pyaudio
import slugify


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
        preslug_name = unicode(self.RE_PRESLUG.sub('', info['name']))
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

    def supports_input_format(self, bits, channels, rate):
        if not self.is_input_device:
            return False
        sample_fmt = self._engine._pyaudio_fmt(bits)
        if not sample_fmt:
            return False
        return self._engine._pyaudio.is_format_supported(
            input_device=self.index,
            input_format=sample_fmt,
            input_channels=channels,
            rate=rate)

    def supports_output_format(self, bits, channels, rate):
        if not self.is_output_device:
            return False
        sample_fmt = self._engine._pyaudio_fmt(bits)
        if not sample_fmt:
            return False
        return self._engine._pyaudio.is_format_supported(
            output_device=self.index,
            output_format=sample_fmt,
            output_channels=channels,
            rate=rate)

    @contextlib.contextmanager
    def _open_stream(self, bits, channels, rate, output=True):
        # Check if format is supported
        unsupported_fmt = ((output and not
                            self.supports_output_format(bits, channels, rate))
                           or
                           (not output and not
                            self.supports_input_format(bits, channels, rate)))
        if unsupported_fmt:
            if output:
                msg_fmt = ("PyAudioDevice {index} ({name}) doesn't support " +
                           "output format (Int{bits}, {channels}-channel at" +
                           " {rate} Hz)")
            else:
                msg_fmt = ("PyAudioDevice {index} ({name}) doesn't support " +
                           "input format (Int{bits}, {channels}-channel at" +
                           " {rate} Hz)")
            msg = msg_fmt.format(index=self.index,
                                 name=self.name,
                                 bits=bits,
                                 channels=channels,
                                 rate=rate)
            self._logger.critical(msg)
            raise UnsupportedFormat(msg)
        # Everything looks fine, open the stream
        stream = self._engine._pyaudio.open(
            format=self._engine._pyaudio_fmt(bits),
            channels=channels,
            rate=rate,
            output=output,
            input=not output,
            frames_per_buffer=1024 if output else 8192)
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

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    audioengine = PyAudioEngine()
    devices = audioengine.get_devices()
    slug_length = max([len(device.slug) for device in devices])
    name_length = max([len(device.name) for device in devices])
    fmt = ('{{index: >2}} {{slug: <{0}}} {{name: <{1}}} {{output: <3}} ' +
           '{{input: <3}}').format(slug_length, name_length)
    print(fmt.format(index="ID", slug="SLUG", name="NAME", output="OUT",
                     input="IN"))
    for device in devices:
        print(fmt.format(index=device.index, name=device.name,
                         slug=device.slug,
                         output="yes" if device.is_output_device else "no",
                         input="yes" if device.is_input_device else "no"))
