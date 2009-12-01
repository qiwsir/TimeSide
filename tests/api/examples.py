from timeside.core import Processor, implements, interfacedoc
from timeside.api import *
from timeside import Metadata
from scikits import audiolab
import numpy

class AudiolabDecoder(Processor):
    """A simple audiolab-based example decoder"""
    implements(IDecoder)

    @staticmethod
    @interfacedoc
    def id():
        return "test_audiolabdec"

    @interfacedoc
    def __init__(self, filename):
        self.file = audiolab.sndfile(filename, 'read')
        self.position = 0

    @interfacedoc
    def output_format(self):
        return (self.file.get_channels(), self.file.get_samplerate())

    @interfacedoc
    def duration(self):
        return self.file.get_nframes() / self.file.get_samplerate()

    @interfacedoc
    def nframes(self):
        return self.file.get_nframes()

    @interfacedoc
    def format(self):
        return self.file.get_file_format()
   
    @interfacedoc
    def encoding(self):
        return self.file.get_encoding()

    @interfacedoc
    def resolution(self):
        resolution = None
        encoding = self.file.get_encoding()

        if encoding == "pcm8":
            resolution = 8
        elif encoding == "pcm16":
            resolution = 16
        elif encoding == "pcm32":
            resolution = 32

        return resolution            

    @interfacedoc
    def metadata(self):
        #TODO
        return Metadata()

    @interfacedoc
    def process(self, frames=None):
        if frames:
            raise Exception("Decoder doesn't accept input frames")

        buffersize = self.buffersize()

        # Need this because audiolab raises a bogus exception when asked
        # to read passed the end of the file
        toread = self.nframes() - self.position
        if toread > buffersize:
            toread = buffersize

        frames = self.file.read_frames(toread)

        self.position += toread

        if toread < buffersize:
            self.file.close()

        return frames

class MaxLevelAnalyzer(Processor):
    implements(IValueAnalyzer)

    @interfacedoc
    def __init__(self):
        self.max_value = 0

    @staticmethod
    @interfacedoc
    def id():
        return "test_maxlevel"

    @staticmethod
    @interfacedoc
    def name():
        return "Max level test analyzer"
   
    @staticmethod
    @interfacedoc
    def unit():
        # power? amplitude?
        return ""

    def process(self, frames=None):        
        max = frames.max()
        if max > self.max_value:
            self.max_value = max

        return frames

    def result(self):
        return self.max_value

class GainEffect(Processor):
    implements(IEffect)

    @interfacedoc
    def __init__(self, gain=1.0):
        self.gain = gain

    @staticmethod
    @interfacedoc
    def id():
        return "test_gain"

    @staticmethod
    @interfacedoc
    def name():
        return "Gain test effect"
   
    def process(self, frames=None):        
        return numpy.multiply(frames, self.gain)

class WavEncoder(Processor):
    implements(IEncoder)

    def __init__(self, output):
        self.file = None
        if isinstance(output, basestring):
            self.filename = output
        else:
            raise Exception("Streaming not supported")
    
    @staticmethod
    @interfacedoc
    def id():
        return "test_wavenc"

    @staticmethod
    @interfacedoc
    def description():
        return "Hackish wave encoder"

    @staticmethod
    @interfacedoc
    def file_extension():
        return "wav"

    @staticmethod
    @interfacedoc
    def mime_type():
        return "audio/x-wav"

    @interfacedoc
    def set_metadata(self, metadata):
        #TODO
        pass

    @interfacedoc
    def process(self, frames):
        if not self.file:
            # Can't open the file in constructor because input_channels and input_samplerate
            # aren't available before set_input_format() has been called
            info = audiolab.formatinfo("wav", "pcm16")
            self.file = audiolab.sndfile(self.filename, "write", format=info, channels=self.input_channels,
                                         samplerate=self.input_samplerate)
        self.file.write_frames(frames)
        if len(frames) < self.buffersize():
            self.file.close()

        return frames            
