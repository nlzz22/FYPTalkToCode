#!/usr/bin/env python3                                                                                
from time import sleep                                                                              
import speech_recognition as sr  
 
# get audio from the microphone                                                                       
r = sr.Recognizer()
# r.energy_threshold = 300 # Recognizer will wait until the audio has an energy above this level (i.e. speaking starts)
with sr.Microphone() as source: r.adjust_for_ambient_noise(source)

print("Minimum energy threshold to {}".format(r.energy_threshold))

count = 0

while True:
    with sr.Microphone() as source:                                                                       
        print("You can start speaking now:")                                                                                   
        audio = r.listen(source)
        print("Analyzing... ")
     
    try:
        # recognize speech using Google Speech Recognition
        read_words = r.recognize_google(audio)

        print("Google : " + read_words + "\n\n")

    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results; {0}".format(e))

    count += 1
    print("Audio read so far : " + str(count))

    try:
        read_words
    except NameError:
        pass
    else:
        if (read_words == "quit"):
            break

    sleep(0.50)

