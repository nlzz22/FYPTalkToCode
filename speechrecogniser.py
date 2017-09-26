import speech_recognition as sr
from os import path

# import from user-defined class
from credentials import APICredentials

def get_voice_input():
        enableGoogle = False
        enableGoogleCloud = False # free 60 mins, $0.006 per 15 seconds thereafter
        enableMicrosoftBing = False # free 5000 transactions, $4 per 1000 transactions thereafter
        
        input_user = raw_input('Type 1 for Google, 2 for Google Cloud: \n')

        # process the API to be used based on user input
        try:
                input_user = int(input_user)
        except ValueError:
                print "input is not a number"
                return None
                
        if (input_user == 1):
                enableGoogle = True
        elif (input_user == 2):
                enableGoogleCloud = True 
        else:
                return None # terminate the program
                                                                      
        r = sr.Recognizer()

        while True:
                input_method = raw_input("Type 1 for Record from voice, 2 for Read from audio file : \n")
                try:
                        input_method = int(input_method)
                        break
                except ValueError:
                        print "input is not a number"
                
        if (input_method == 1):
                # record from voice
                audio = read_from_microphone(r)
        elif (input_method == 2):
                # read from audio file
                audio = read_from_audio_file(r)
        else:
                return None # terminate the program

        print "Analyzing..."


        # Recognize the speech         
        try:
                if (enableGoogle):
                        # recognize speech using Google Speech Recognition
                        read_words = r.recognize_google(audio)
                        print("Google finished deciphering ! \n")
                        return read_words

                if (enableGoogleCloud):
                        # recognize speech using Google Cloud Speech Recognition
                        credential_object = APICredentials()
                        google_cloud_json = credential_object.get_google_json_file()
                        preferred_phrases = ["equal", "if", "then", "else", "end", "declare integer", "integer", "boolean", \
                                             "declare boolean", "declare string", "declare float", "declare double", "declare character", \
                                             "string", "float", "double", "character", "size", "index", "create function", \
                                             "function", "return", "return type", "parameter", "call", "for", "plus", "plus plus", \
                                             "minus", "minus minus", "times", "divide", "while", "switch", "case", "dot", "end if", \
                                             "end switch", "end declare", "for loop", "end equal"]

                        read_words_google = r.recognize_google_cloud(audio, google_cloud_json, "en-US", preferred_phrases, False)
                        print("Google Cloud finished deciphering ! \n")
                        return read_words_google

                if (enableMicrosoftBing):
                        # recognize speech using Microsoft Bing Speech Recognition
                        credential_object = APICredentials()
                        bing_key = credential_object.get_bing_key()

                        read_words_bing = r.recognize_bing(audio, bing_key, "en-US", False)
                        print("Microsoft Bing : " + read_words_bing + "\n\n")               

        except sr.UnknownValueError:
                print("Could not understand audio")
        except sr.RequestError as e:
                print("Could not request results; {0}".format(e))

def read_from_microphone(r):
        print "Reading from microphone selected! \n"
        print "Adjusting for environment ambient noise ... \n"
        with sr.Microphone() as source: r.adjust_for_ambient_noise(source)

        print("Minimum energy threshold to {}".format(r.energy_threshold))

        with sr.Microphone() as source:                                                                       
                print("You can start speaking now:")                                                                                   
                audio = r.listen(source)
                return audio


def read_from_audio_file(r):
        print "Reading from audio file selected! \n"
        input_filename = raw_input('Please enter the filename (Work\\...\\filenamewithoutwav) : \n')
        
        print "Reading from audio file..."
        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "TestSamples\\" + input_filename + ".wav")

        with sr.AudioFile(AUDIO_FILE) as source:
                audio = r.record(source)  # read the entire audio file
                return audio
