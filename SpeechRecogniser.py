#!/usr/bin/env python2

import speech_recognition as sr
from speech_recognition import * 
from os import path
from os import sep
import threading
from threading import Thread
import time
import audioop
from Keywords import Keywords

# import from user-defined class
from credentials import APICredentials

class SpeechRecognitionModule:
        MIN_REQUIRED_ENERGY = 500
        
        def __init__(self):
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone()
            self.has_adjusted_for_voice = False
            credential_object = APICredentials()
            self.google_cloud_json = credential_object.get_google_json_file()

            kw = Keywords()
            self.preferred_phrases = kw.get_preferred_phrases()

        def print_feedback_one(self, feedback, uiThread):
            uiThread.UpdateFeedbackOne(feedback)

        def print_feedback_two(self, feedback, uiThread):
            uiThread.UpdateFeedbackTwo(feedback)

        def print_feedback_three(self, feedback, uiThread):
            uiThread.UpdateFeedbackThree(feedback)

        def print_feedback_four(self, feedback, uiThread):
            uiThread.UpdateFeedbackFour(feedback)

        def print_feedback_five(self, feedback, uiThread):
            uiThread.UpdateFeedbackFive(feedback)

        def print_speak_now(self, feedback, uiThread):
            uiThread.UpdateSpeakNow(feedback)

        def persistent_listen(self, timeout=None, phrase_time_limit=None):
                r = sr.Recognizer()
                r.energy_threshold = 1000
                m = sr.Microphone()

                while not self.is_hotword_found:
                        with m as source:
                                audio = None
                                try:
                                        self.persist_listen_lock.acquire()
                                        audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                                        self.persist_listen_lock.release()
                                except WaitTimeoutError:
                                        audio = None
                                        try:
                                                self.persist_listen_lock.release()
                                        except:
                                                pass
                                if audio is not None:
                                        self.record_buffer_lock.acquire()
                                        self.record_buffer.append(audio)
                                        self.record_buffer_lock.release()
        
        def recognize_keyword(self, recognizer):
            keyword_entries = [["start recording", 1e-3], ["ah", 1e-49], ["start rack cording", 1e-4], ["stuck recording", 1e-4] ,\
                       ["stott reporting", 1e-5], ["saw ray clothing", 1e-5]]
            #[["start recording", 1e-48], ["stop", 1e-49], ["run", 1e-49], [" ", 1e-48]]

            while not self.is_hotword_found:
                    self.record_buffer_lock.acquire()
                    if len(self.record_buffer) > 0:
                            audio = self.record_buffer.pop(0)
                            self.record_buffer_lock.release()
                    else:
                            self.record_buffer_lock.release()
                            continue
                    try:
                        text = recognizer.recognize_sphinx(audio, keyword_entries=keyword_entries) # use offline sphinx recognition.
                        lower_text = text.lower().replace("ah", "").strip()
                        # recognizing hotword: if there exists some words, except for the word `ah`
                        # it means that there is some hotword found which sounds like `start recording`
                        if len(lower_text) > 0:
                                self.is_hotword_found = True
                    except sr.UnknownValueError as f:
                        self.error_counter += 1
                    except sr.RequestError as e:
                        self.error_counter += 1
                    finally:
                        if self.error_counter >= 10:
                                self.error_counter = 0
                                print ("Unknown values read by the recognizer")

        def wait_for_hotword(self, uiThread):
                self.record_buffer = []
                self.record_buffer_lock = threading.Lock()
                self.persist_listen_lock = threading.Lock()
                self.error_counter = 0
                self.is_hotword_found = False

                r = sr.Recognizer()

                RECORD_THREAD_TIMEOUT = 0.5
                RECORD_THREAD_PHRASE_LIMIT = 3
                recording_thread = Thread(target=self.persistent_listen, \
                                          args = (RECORD_THREAD_TIMEOUT, RECORD_THREAD_PHRASE_LIMIT))
                recording_thread2 = Thread(target=self.persistent_listen, \
                                          args = (RECORD_THREAD_TIMEOUT, RECORD_THREAD_PHRASE_LIMIT))
                recording_thread.start()
                recording_thread2.start()

                self.print_feedback_two("Waiting for hotword `start recording` before we resume recording...", uiThread)
                self.print_speak_now("SAY 'start recording'", uiThread)
                self.print_feedback_one("", uiThread)
                self.print_feedback_five("Please keep quiet for 1 second before saying 'start recording'", uiThread)

                recognize_threads = [1,2,3]
                for i in range(3):
                        recognize_threads[i] = Thread(target=self.recognize_keyword, args = (r,))
                        recognize_threads[i].start()

                # repeatedly wait for hotword
                while (True):
                        if self.is_hotword_found:
                                self.print_feedback_five("", uiThread)
                                break

        def get_sound_energy(self, mic, queue):
                while True:
                        with mic as source:
                                buffer = source.stream.read(source.CHUNK)
                                energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
                        queue.put(energy)
                        
                

        # api: 1 for Google, 2 for Google Cloud
        def decipher_audio_with_api(self, audio, variables_list, uiThread, api):
                # Recognize the speech         
                try:
                        if (api == 1):
                                # recognize speech using Google Speech Recognition
                                read_words = self.recognizer.recognize_google(audio)
                                self.print_feedback_five("Google finished deciphering !", uiThread)
                                return read_words        
                        elif (api == 2):
                                # recognize speech using Google Cloud Speech Recognition
                                current_preferred_phrases = self.preferred_phrases + variables_list
                                
                                read_words_google = RecognizerGA().recognize_google_cloud( \
                                        audio, self.google_cloud_json, "en-US", current_preferred_phrases, False)
                                
                                self.print_feedback_five("Google Cloud finished deciphering !", uiThread)
                                return read_words_google
                        else:
                                print ("Error: unknown api constant found at SpeechRecogniser.py")

                except sr.UnknownValueError:
                        self.print_feedback_one("Could not understand audio", uiThread)
                except sr.RequestError as e:
                        self.print_feedback_one("Could not request results; {0}".format(e), uiThread)
                

        def read_from_microphone(self, uiThread, timeout=None, phrase_time_limit=None):
                if not self.has_adjusted_for_voice:
                        self.print_feedback_two("Please wait while we detect environment noise ...", uiThread)
                        with self.mic as source: self.recognizer.adjust_for_ambient_noise(source)

                        # Adjusts the energy threshold level.
                        self.recognizer.energy_threshold = max( \
                                self.recognizer.energy_threshold, SpeechRecognitionModule.MIN_REQUIRED_ENERGY)
                        
                        string_to_show = "Environment energy is {}".format(int(self.recognizer.energy_threshold))
                        self.recog_thresh = self.recognizer.energy_threshold
                        self.print_feedback_two(string_to_show, uiThread)
                        self.print_speak_now("SPEAK NOW", uiThread)
                        self.has_adjusted_for_voice = True
                else:
                        self.recognizer.energy_threshold = self.recog_thresh
                        string_to_show = "Environment energy is {}".format(int(self.recog_thresh))
                        self.print_feedback_two(string_to_show, uiThread)
                        self.print_speak_now("SPEAK NOW", uiThread)

                with self.mic as source:
                        audio = None
                        try:
                                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                        except WaitTimeoutError:
                                audio = None
                        return audio


        def read_from_audio_file(self, uiThread):
                self.print_feedback_two("Reading from audio file selected! ", uiThread)
                input_filename = raw_input('Please enter the filename (Work/.../filenamewithoutwav) : \n')
                parts = input_filename.split("/")
                input_filename = sep.join(parts)
                
                self.print_feedback_two("Reading from audio file, please wait...", uiThread)
                AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "TestSamples", input_filename + ".wav")

                with sr.AudioFile(AUDIO_FILE) as source:
                        audio = self.recognizer.record(source)  # read the entire audio file
                        return audio


# This inherits the parent Recognizer class so we can override its functions
class RecognizerGA( Recognizer ):
        # this is needed because of google cloud speech migration to GA
        def recognize_google_cloud(self, audio_data, credentials_json=None, language="en-US", preferred_phrases=None, show_all=False):
                """
                Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Google Cloud Speech API.
                This function requires a Google Cloud Platform account; see the `Google Cloud Speech API Quickstart <https://cloud.google.com/speech/docs/getting-started>`__ for details and instructions. Basically, create a project, enable billing for the project, enable the Google Cloud Speech API for the project, and set up Service Account Key credentials for the project. The result is a JSON file containing the API credentials. The text content of this JSON file is specified by ``credentials_json``. If not specified, the library will try to automatically `find the default API credentials JSON file <https://developers.google.com/identity/protocols/application-default-credentials>`__.
                The recognition language is determined by ``language``, which is a BCP-47 language tag like ``"en-US"`` (US English). A list of supported language tags can be found in the `Google Cloud Speech API documentation <https://cloud.google.com/speech/docs/languages>`__.
                If ``preferred_phrases`` is a list of phrase strings, those given phrases will be more likely to be recognized over similar-sounding alternatives. This is useful for things like keyword/command recognition or adding new phrases that aren't in Google's vocabulary. Note that the API imposes certain `restrictions on the list of phrase strings <https://cloud.google.com/speech/limits#content>`__.
                Returns the most likely transcription if ``show_all`` is False (the default). Otherwise, returns the raw API response as a JSON dictionary.
                Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError`` exception if the speech recognition operation failed, if the credentials aren't valid, or if there is no Internet connection.
                """
                
                assert isinstance(audio_data, AudioData), "``audio_data`` must be audio data"
                if credentials_json is not None:
                    try: json.loads(credentials_json)
                    except: raise AssertionError("``credentials_json`` must be ``None`` or a valid JSON string")
                assert isinstance(language, str), "``language`` must be a string"
                assert preferred_phrases is None or all(isinstance(preferred_phrases, (type(""), type(u""))) for preferred_phrases in preferred_phrases), "``preferred_phrases`` must be a list of strings"

                # See https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionConfig
                flac_data = audio_data.get_flac_data(
                    convert_rate=None if 8000 <= audio_data.sample_rate <= 48000 else max(8000, min(audio_data.sample_rate, 48000)),  # audio sample rate must be between 8 kHz and 48 kHz inclusive - clamp sample rate into this range
                    convert_width=2  # audio samples must be 16-bit
                )

                try:
                    from oauth2client.client import GoogleCredentials
                    from googleapiclient.discovery import build
                    import googleapiclient.errors

                    # cannot simply use 'http = httplib2.Http(timeout=self.operation_timeout)'
                    # because discovery.build() says 'Arguments http and credentials are mutually exclusive'
                    import socket
                    import googleapiclient.http
                    if self.operation_timeout and socket.getdefaulttimeout() is None:
                        # override constant (used by googleapiclient.http.build_http())
                        googleapiclient.http.DEFAULT_HTTP_TIMEOUT_SEC = self.operation_timeout

                    if credentials_json is None:
                        api_credentials = GoogleCredentials.get_application_default()
                    else:
                        # the credentials can only be read from a file, so we'll make a temp file and write in the contents to work around that
                        with PortableNamedTemporaryFile("w") as f:
                            f.write(credentials_json)
                            f.flush()
                            api_credentials = GoogleCredentials.from_stream(f.name)

                    speech_service = build("speech", "v1", credentials=api_credentials, cache_discovery=False)
                except ImportError:
                    raise RequestError("missing google-api-python-client module: ensure that google-api-python-client is set up correctly.")

                if preferred_phrases is None:
                    speech_config = {"encoding": "FLAC", "sampleRateHertz": audio_data.sample_rate, "languageCode": language}
                else:
                    speech_config = {"encoding": "FLAC", "sampleRateHertz": audio_data.sample_rate, "languageCode": language, "speechContexts": {"phrases": preferred_phrases}}
                request = speech_service.speech().recognize(body={"audio": {"content": base64.b64encode(flac_data).decode("utf8")}, "config": speech_config})

                try:
                    response = request.execute()
                except googleapiclient.errors.HttpError as e:
                    raise RequestError(e)
                except URLError as e:
                    raise RequestError("recognition connection failed: {0}".format(e.reason))

                if show_all: return response
                if "results" not in response or len(response["results"]) == 0: raise UnknownValueError()
                transcript = ""
                for result in response["results"]:
                    transcript += result["alternatives"][0]["transcript"].strip() + " "

                return transcript

