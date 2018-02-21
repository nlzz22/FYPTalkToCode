#!/usr/bin/env python2

import json
#from pprint import pprint

class APICredentials:
    GOOGLE_CREDENTIAL_FILE = "SpeechRecognition-8e50e15b5266.json"

    def get_google_json_file(self):
        with open(self.GOOGLE_CREDENTIAL_FILE) as file:
            return json.dumps(json.load(file))
