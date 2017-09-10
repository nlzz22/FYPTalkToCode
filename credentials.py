import json
#from pprint import pprint

class APICredentials:
    GOOGLE_CREDENTIAL_FILE = "SpeechRecognition-8e50e15b5266.json"
    BING_FILE = "Bing.txt"

    def get_google_json_file(self):
        with open(self.GOOGLE_CREDENTIAL_FILE) as file:
            return json.dumps(json.load(file))

    def get_bing_key(self):
        with open(self.BING_FILE) as file:
            return file.readline()
