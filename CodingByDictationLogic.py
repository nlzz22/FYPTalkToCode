import os
import wx
from SpeechRecogniser import SpeechRecognitionModule as SpeechReader
from WordCorrector import WordCorrector
from NewWordParser import WordParser as newWordParser
from NewWordParser import Stack
import StructuralCommandParser as scParser
from TextFileReader import TextFileReader
from Logger import Logger
from StandardFunctions import StandardFunctions
import time
import threading
from threading import Thread

class HotwordRecognition(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui

    def run(self):
        self.speechReader = SpeechReader()
        self.speechReader.wait_for_hotword(self.ui) # blocks till hotword found.

        self.ui.startRecording()

        

class CodingByDictationLogic:
    ##########################################
    ###### DO NOT TOUCH THESE CONSTANTS ######
    # read from constants
    READ_FROM_SPEECH = 1
    READ_FROM_AUDIO_FILE = 2
    READ_FROM_TYPING = 3
    READ_FROM_TEXT_FILE = 4

    # api used constants
    GOOGLE = 1
    GOOGLE_CLOUD = 2

    # constants in-built
    VOICE = 1
    AUDIO_FILE = 2
    ##########################################
    ##########################################
    
    def __init__(self):
        # EDIT THIS ONLY.
        # User defined: Method of reading here.
        self.read_from = CodingByDictationLogic.READ_FROM_SPEECH
        self.api_used = CodingByDictationLogic.GOOGLE_CLOUD
        self.text_filename = "FindMaximum.txt" # default is "FindMaximum.txt"

        self.variables_stack = Stack()
        self.text_history_stack = Stack()
        self.code_stack = Stack()
        self.accepted_indices = []
        self.current_index = 0
        self.std_funcs = StandardFunctions().get_std_functions()

        self.logger = Logger()

        self.voice_lock = threading.Lock()

    def print_history_text(self, uiThread):
        hist_text = ""
        curr_index = 0
        for i in range(0, len(self.text_history_stack.stack)):
            if curr_index < len(self.accepted_indices) and i == self.accepted_indices[curr_index]:
                hist_text += self.text_history_stack.stack[i] + "\n"
                curr_index += 1
            else:
                hist_text += self.text_history_stack.stack[i] + " "   
        
        uiThread.UpdateHistoryBody(hist_text)

    def print_code(self, to_add_corrected, parsed_sc, wordParser, scParser, uiThread):
        accepted_text_list = []
        curr_text = ""
        curr_index = 0
        for i in range(0, len(self.text_history_stack.stack)):
            if curr_index < len(self.accepted_indices) and i == self.accepted_indices[curr_index]:
                curr_text += self.text_history_stack.stack[i] + " "
                curr_index += 1
                accepted_text_list.append(curr_text)
                curr_text = ""
            else:
                curr_text += self.text_history_stack.stack[i] + " "

        structured_command = self.get_struct_command_from_text_list(wordParser, accepted_text_list)
        if to_add_corrected:
            structured_command += " " + parsed_sc
        code = scParser.parse_structural_command_to_code(structured_command)
      
        uiThread.UpdateCodeBody(code)
        self.code_stack.push(code)

    def print_latest_code(self, uiThread):
        code = self.code_stack.peek()
        if code is None:
            uiThread.UpdateCodeBody("No code has been generated yet.")
        else:
            uiThread.UpdateCodeBody(code)

    def print_feedback_one(self, feedback, uiThread):
        uiThread.UpdateFeedbackOne(feedback)

    def print_feedback_two(self, feedback, uiThread):
        uiThread.UpdateFeedbackTwo(feedback)

    def print_feedback_three(self, feedback, uiThread):
        uiThread.UpdateFeedbackThree(feedback)

    def get_struct_command_from_text_list(self, wordParser, text_list):
        struct_command_list = []
        
        for text in text_list:
            structured_command = wordParser.parse(text, False)
            struct_command_list.append(structured_command)
        return " ".join(struct_command_list)

    def build_var_list_from_stack(self, stackClass):
        temp_set = set()
        for curr_var_list in stackClass.stack:
            for variable in curr_var_list:
                temp_set.add(variable)

        # add standard function calls
        for std_func in self.std_funcs:
            temp_set.add(std_func)  

        return list(temp_set)

    def build_string_from_stack(self, stackClass, accepted_indices):
        joined_string = ""
        if len(accepted_indices) == 0:
            last_accepted_index = -1
        else:
            last_accepted_index = accepted_indices[len(accepted_indices) - 1]

        for i in range(last_accepted_index + 1, len(stackClass.stack)):
            joined_string += stackClass.stack[i] + " "
        return joined_string

    # This function prints all variables in the stack, for debug purposes only.
    def print_all_var(self):
        for var in self.variables_stack.stack:
            print var
        print "\n"

    def undo(self, to_continue_reading=False):
        if to_continue_reading:
            self.unlock_voice(self.uiThread)
        if self.current_index > 0:
            self.variables_stack.pop()
            undo_text = self.text_history_stack.pop()
            self.code_stack.pop()

            if len(self.accepted_indices) > 0:
                last_accepted_index = self.accepted_indices[len(self.accepted_indices) - 1]
                if self.current_index - 1 == last_accepted_index:
                    self.accepted_indices.pop()

            self.current_index -= 1
            self.print_history_text(self.uiThread)
            self.print_latest_code(self.uiThread)
            self.print_feedback_one("Your undo is registered for " + str(undo_text), self.uiThread)
        else:
            self.print_feedback_one("There is nothing to undo.", self.uiThread)

    def lock_voice(self, uiThread):
        uiThread.OffRecordingMode()
        # run program to wait for hotword
        hotwordRecognizer = HotwordRecognition(ui=uiThread)
        hotwordRecognizer.start()
        
    def unlock_voice(self, uiThread):
        uiThread.OnRecordingMode()
        self.release_voice_lock()

    def release_voice_lock(self):
        try:
            self.voice_lock.release()
        except:
            pass

    def main(self, uiThread):
        to_continue_reading = True
        self.uiThread = uiThread
        
        speechReader = SpeechReader()
        wordParser = newWordParser()
        fileReader = TextFileReader(self.text_filename)
        
        while to_continue_reading:
            self.voice_lock.acquire()
            variables_list = self.build_var_list_from_stack(self.variables_stack)
            
            # Speech to text
            if self.read_from == CodingByDictationLogic.READ_FROM_SPEECH:
                read_words = speechReader.get_voice_input(variables_list, self.api_used, CodingByDictationLogic.VOICE, uiThread)
            elif self.read_from == CodingByDictationLogic.READ_FROM_AUDIO_FILE:
                read_words = speechReader.get_voice_input(variables_list, self.api_used, CodingByDictationLogic.AUDIO_FILE, uiThread)
            elif self.read_from == CodingByDictationLogic.READ_FROM_TYPING:
                read_words = raw_input("Type in speech : ")
            elif self.read_from == CodingByDictationLogic.READ_FROM_TEXT_FILE:
                read_words = fileReader.read_line()
                if read_words == "": # EOF
                    to_continue_reading = False
                    
            else:
                self.print_feedback_one("Error: unknown read_from detected", uiThread)
                return None # terminate the program

            if (read_words is None):
                self.print_feedback_one("Invalid input when reading", uiThread)
                # time.sleep(2)
                self.lock_voice(uiThread)
                continue

            # text to processed_text
            wordCorrector = WordCorrector(read_words, variables_list)
            corrected = wordCorrector.run_correction()

            if corrected.strip() == "undo":
                self.undo(True)
                continue

            # processed_text to structured_command / code and display to user.
            text_to_parse = self.build_string_from_stack(self.text_history_stack, self.accepted_indices) + " " + str(corrected)

            error_message = ""
            potential_missing = ""
            structured_command = ""

            try:
                structured_command = wordParser.parse(text_to_parse, True)
            except Exception as ex:
                self.print_feedback_one("Unable to understand : " + str(corrected), uiThread)
                self.lock_voice(uiThread)
                continue

            self.release_voice_lock()

            to_add_corrected = False
            if structured_command == "": # cannot parse
                result_struct = wordParser.parse_with_correction(text_to_parse)

                if "expected" in result_struct.keys():
                    error_message = result_struct["expected"]
                if "potential_missing" in result_struct.keys():
                    potential_missing = result_struct["potential_missing"]
                if "variables" in result_struct.keys() and len(result_struct["variables"]) != 0:
                    self.variables_stack.push(result_struct["variables"])
                else:
                    self.variables_stack.push([])

                to_add_corrected = True
                parsed = result_struct["parsed"]
            else: # can parse
                parsed = structured_command
                self.variables_stack.push(wordParser.get_variables())
                self.accepted_indices.append(self.current_index)
           
            sample_code = scParser.parse_structural_command_to_code(parsed)

            # Feedback to user
            if error_message != "":
                if potential_missing != "":
                    self.print_feedback_one("Expected  : " + potential_missing, uiThread)
                else:
                    if error_message.strip() == "Expected":
                        self.print_feedback_one("Incomplete statement.", uiThread)
                    else:
                        self.print_feedback_one("Error     : " + error_message, uiThread)
            else:
                self.print_feedback_one(" ", uiThread)

            # printlines for debug
            print "Audio read by Speech Recognizer : " + read_words
            print "Processed text after correction : " + corrected
            self.logger.log(read_words + " --> " + corrected)

            self.print_feedback_two("Read: " + corrected, uiThread)

            if self.read_from == CodingByDictationLogic.READ_FROM_TEXT_FILE:
                if to_continue_reading == True:
                    input_continue = "y"
                else:
                    input_continue = "d"
            else:
                input_continue = "y"
            
            if input_continue.lower() == "y":
                # Accept and continue
                to_continue_reading = True
                self.current_index += 1

                self.text_history_stack.push(str(corrected))
            elif input_continue.lower() == "d":
                # Accept and stop
                to_continue_reading = False

                self.text_history_stack.push(str(corrected))
            else:
                to_continue_reading = False # else reject and stop

            self.print_history_text(uiThread)
            self.print_code(to_add_corrected, parsed, wordParser, scParser, uiThread)
            # self.print_all_var() # for debug only.

