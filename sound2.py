import speech_recognition as sr
from speech_recognition import *
import audioop

r = sr.Recognizer()
m = sr.Microphone()
buffer = b""
assert isinstance(m, AudioSource), "m must be audio source"


while True:
    with m as source:
        buffer = source.stream.read(source.CHUNK)
        energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
        
        print energy
    
