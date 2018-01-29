import speech_recognition as sr
from speech_recognition import * 
from os import path

# import from user-defined class
from credentials import APICredentials

class SpeechRecognitionModule:
        def __init__(self):
            self.recognizer = sr.Recognizer()
            self.has_adjusted_for_voice = False
            credential_object = APICredentials()
            self.google_cloud_json = credential_object.get_google_json_file()
            self.preferred_phrases = ["equal", "if", "then", "else", "end", "declare integer", "integer", "boolean", \
                                 "declare boolean", "declare string", "declare float", "declare double", "declare character", \
                                 "string", "float", "double", "character", "size", "index", "create function", \
                                 "function", "return", "return type", "parameter", "call function", "for", "plus", "plus plus", \
                                 "minus", "minus minus", "times", "divide", "while", "switch", "case", "dot", "end if", \
                                 "end switch", "end declare", "for loop", "end equal", "for loop condition i", "end while", \
                                 "end string", "undo", "default", "break", "and", "or", "symbol", "ampersand", \
                                 "percent", "dollar", "backslash", "colon", "print f", "scan f", "continue"]

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

        def wait_for_hotword(self, uiThread):
                self.error_counter = 0
                
                self.is_hotword_found = False
                def recognize_keyword(recognizer, audio):
                    try:
                        text = recognizer.recognize_google(audio) # use normal google recognition.
                        lower_text = text.lower()
                        if "record" in lower_text or "caught" in lower_text: # recognizing `record` and its misrecognized words.
                                self.is_hotword_found = True
                        else:
                                print ("Debug: wait_for_hotword found " + text)
                    except sr.UnknownValueError:
                        self.error_counter += 1
                    except sr.RequestError as e:
                        self.error_counter += 1
                    finally:
                        if self.error_counter >= 10:
                                self.error_counter = 0
                                print ("Unknown values read by the recognizer")

                r = sr.Recognizer()
                m = sr.Microphone()
                
                with m as source:
                    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

                self.print_feedback_two("Waiting for hotword `record` before we resume recording...", uiThread)
                self.print_feedback_one("", uiThread)
                self.print_feedback_five("", uiThread)

                # start listening in the background
                stop_listening = r.listen_in_background(m, recognize_keyword, phrase_time_limit=1)
                # `stop_listening` is now a function that, when called, stops background listening

                # repeatedly wait for hotword
                while (True):
                        if self.is_hotword_found:
                                break

                # calling this function requests that the background listener stop listening
                stop_listening(wait_for_stop=False)

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
                        with sr.Microphone() as source: self.recognizer.adjust_for_ambient_noise(source)
                        string_to_show = "Environment energy is {}, Start speaking ... ".format(int(self.recognizer.energy_threshold))
                        self.print_feedback_two(string_to_show, uiThread)
                        self.has_adjusted_for_voice = True
                else:
                        self.print_feedback_two("Please continue speaking...", uiThread)

                with sr.Microphone() as source:
                        audio = None
                        try:
                                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                        except WaitTimeoutError:
                                audio = None
                        return audio


        def read_from_audio_file(self, uiThread):
                self.print_feedback_two("Reading from audio file selected! ", uiThread)
                input_filename = raw_input('Please enter the filename (Work\\...\\filenamewithoutwav) : \n')
                
                self.print_feedback_two("Reading from audio file, please wait...", uiThread)
                AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "TestSamples\\" + input_filename + ".wav")

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

