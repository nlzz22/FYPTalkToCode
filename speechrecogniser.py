import speech_recognition as sr
from os import path

# import from user-defined class
from credentials import APICredentials

def main():
        enableGoogle = False
        enableGoogleCloud = False # free 60 mins, $0.006 per 15 seconds thereafter
        enableMicrosoftBing = False # free 5000 transactions, $4 per 1000 transactions thereafter
        
        input_user = raw_input('Type 1 for Google, 2 for Google Cloud, 3 for Microsoft Bing, 4 to terminate : \n')

        # process the API to be used based on user input
        try:
                input_user = int(input_user)
        except ValueError:
                print "input is not a number"
                main()
                return None # terminate the program
                
        while (input_user > 0):
                num = input_user % 10

                if (num == 1):
                        enableGoogle= True
                elif (num == 2):
                        enableGoogleCloud = True
                elif (num == 3):
                        enableMicrosoftBing = True
                elif (num == 4):
                        return None
                
                input_user /= 10
                                                                      
        r = sr.Recognizer()

        # get audio from the microphone
##        print "Adjusting for environment ambient noise ... \n"
##        with sr.Microphone() as source: r.adjust_for_ambient_noise(source)
##
##        print("Minimum energy threshold to {}".format(r.energy_threshold))
##
##        with sr.Microphone() as source:                                                                       
##                print("You can start speaking now:")                                                                                   
##                audio = r.listen(source)
##                print("Analyzing... ")

        # get audio from the audio file
        input_filename = raw_input('Please enter the filename : \n')
        
        print "Reading from audio file..."
        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "TestSamples\\" + input_filename + ".wav")

        with sr.AudioFile(AUDIO_FILE) as source:
            audio = r.record(source)  # read the entire audio file
        print "Analyzing..."


        # Recognize the speech         
        try:
                if (enableGoogle):
                        # recognize speech using Google Speech Recognition
                        read_words = r.recognize_google(audio)
                        print("Google : " + read_words + "\n\n")

                if (enableGoogleCloud):
                        # recognize speech using Google Cloud Speech Recognition
                        credential_object = APICredentials()
                        google_cloud_json = credential_object.get_google_json_file()
                        preferred_phrases = ["equal", "if", "then", "else", "end", "declare integer", "integer", "boolean", \
                                             "declare boolean", "declare string", "declare float", "declare double", "declare character", \
                                             "string", "float", "double", "character", "size", "index", "create function", \
                                             "function", "return", "return type", "parameter", "call", "for", "plus", "plus plus", \
                                             "minus", "minus minus", "times", "divide", "while", "switch", "case", "dot", "end if", \
                                             "end switch"]

                        read_words_google = r.recognize_google_cloud(audio, google_cloud_json, "en-US", preferred_phrases, False)
                        print("Google Cloud : " + read_words_google + "\n\n")

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

        main() # recursive call 

# Run the main function
main()
