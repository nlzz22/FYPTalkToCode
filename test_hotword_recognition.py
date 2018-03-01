import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
r.energy_threshold = 1000

while True:
    with sr.Microphone() as source:
        #print("Say something!")
        try:
            audio = r.listen(source,timeout=0.1,phrase_time_limit =3)
        except:
            continue

    # recognize speech using Sphinx
    keyword_entries = [["start recording", 1e-3], ["ah", 1e-49], ["start rack cording", 1e-4], ["stuck recording", 1e-4] ,\
                       ["stott reporting", 1e-5], ["saw ray clothing", 1e-5]]

    try:
        a =  r.recognize_sphinx(audio, keyword_entries=keyword_entries)
        print a 
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))
