#!/usr/bin/env python2

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
import copy
import Queue

class HotwordRecognition(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui

    def run(self):
        self.speechReader = SpeechReader()
        self.ui.ShowVisualizer(False)
        self.speechReader.wait_for_hotword(self.ui) # blocks till hotword found.

        self.ui.startRecording()

class SoundEnergyReader(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.energy_reader = SpeechReader() 
        self.queue_buffer = Queue.Queue()
        self.ui = ui

    def run(self):
        retriever_thread = Thread(target=self.energy_reader.get_sound_energy, args=(self.energy_reader.mic, self.queue_buffer,))
        passer_thread = Thread(target=self.pass_energy)
        retriever_thread.start()
        passer_thread.start()

    def pass_energy(self):
        counter = 0
        sum_en = 0
        while True:
            sum_en += self.queue_buffer.get()
            counter += 1
            if counter > 2:
                counter = 0
                self.ui.PassSoundEnergyValue(sum_en / 3)
                sum_en = 0



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
    
    def __init__(self, uiThread):
        # EDIT THIS ONLY.
        # User defined: Method of reading here.
        self.read_from = CodingByDictationLogic.READ_FROM_SPEECH
        self.api_used = CodingByDictationLogic.GOOGLE_CLOUD
        self.text_filename = "FindMaximum.txt" # default is "FindMaximum.txt"
        self.to_show_time = False

        self.variables_stack = Stack()
        self.text_history_stack = Stack()
        self.code_stack = Stack()
        self.accepted_indices = []
        self.current_index = 0
        self.std_funcs = StandardFunctions().get_std_functions()
        self.error_from_scparser = False
        self.create_func_complete = Stack()

        self.logger = Logger()

        self.voice_lock = threading.Lock()
        self.buffer_semaphore = threading.Lock()
        self.audio_count = 0
        self.audio_count_semaphore = threading.Lock()

        self.buffer = []
        self.hotwordRecognizer = None

        self.soundEnergyReader = SoundEnergyReader(ui=uiThread)
        self.soundEnergyReader.start()

    def print_history_text(self, uiThread):
        hist_text = ""
        curr_index = 0
        last = ""
        len_text_hist_stack = len(self.text_history_stack.stack)
        for i in range(0, len_text_hist_stack - 1):
            if curr_index < len(self.accepted_indices) and i == self.accepted_indices[curr_index]:
                hist_text += self.text_history_stack.stack[i] + "\n\n"
                curr_index += 1
            else:
                hist_text += self.text_history_stack.stack[i] + "\n"
        if len_text_hist_stack > 0:
            last = self.text_history_stack.stack[len_text_hist_stack - 1]
        else:
            last = ""
        
        uiThread.UpdateHistoryBody(hist_text, last)

    def print_code(self, to_add_corrected, parsed_sc, wordParser, uiThread):
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

        structured_command = ""
        try:
            structured_command = self.get_struct_command_from_text_list(wordParser, accepted_text_list)
            if to_add_corrected:
                structured_command += " " + parsed_sc
        except:
            structured_command = ""
        
        code = scParser.parse_structural_command_to_code(structured_command)
        
        if scParser.SPECIAL_REJECT_SEQ in code:
            # Error found when parsing with sc parser.
            self.print_feedback_one("Error detected when converting to code, please undo.", uiThread)
            prev_code = self.code_stack.peek()
            self.code_stack.push(prev_code)
            self.error_from_scparser = True
        else:
            # Conversion is good with sc parser.
            uiThread.UpdateCodeBody(code)
            self.code_stack.push(code)
            self.error_from_scparser = False

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

    def print_feedback_four(self, feedback, uiThread):
        uiThread.UpdateFeedbackFour(feedback)

    def print_feedback_five(self, feedback, uiThread):
        uiThread.UpdateFeedbackFive(feedback)

    def print_speak_now(self, feedback, uiThread):
        uiThread.UpdateSpeakNow(feedback)

    def get_struct_command_from_text_list(self, wordParser, text_list):
        struct_command_list = []
        
        for text in text_list:
            res = wordParser.parse(text)
            structured_command = res["parsed"][0]
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
            self.create_func_complete.pop()

            if len(self.accepted_indices) > 0:
                last_accepted_index = self.accepted_indices[len(self.accepted_indices) - 1]
                if self.current_index - 1 == last_accepted_index:
                    self.accepted_indices.pop()

            self.current_index -= 1
            self.print_history_text(self.uiThread)
            self.print_latest_code(self.uiThread)
            self.print_feedback_four("Your undo is registered for " + str(undo_text), self.uiThread)
        else:
            self.print_feedback_four("There is nothing to undo.", self.uiThread)

    def clear(self):
        self.current_index = 0
        self.variables_stack = Stack()
        self.text_history_stack = Stack()
        self.code_stack = Stack()
        self.accepted_indices = []
        self.current_index = 0
        self.create_func_complete = Stack()

        self.print_history_text(self.uiThread)
        self.print_latest_code(self.uiThread)
        self.print_feedback_four("You have cleared everything. ", self.uiThread)

    def lock_voice(self, uiThread):
        self.voice_lock.acquire()
        uiThread.OffRecordingMode()
        self.audio_count_semaphore.acquire()
        self.audio_count = 0
        self.print_feedback_three("Audio waiting for processing : 0", uiThread)
        self.audio_count_semaphore.release()
        
        self.buffer_semaphore.acquire()
        self.buffer = []
        try:
            self.buffer_semaphore.release()
        except:
            self.logger.log("buffer semaphore released without acquire @ lock_voice")
         
        # run program to wait for hotword
        self.hotwordRecognizer = HotwordRecognition(ui=uiThread)
        self.hotwordRecognizer.start()
        
    def unlock_voice(self, uiThread):
        uiThread.OnRecordingMode()
        self.release_voice_lock()

    def release_voice_lock(self):
        try:
            self.voice_lock.release()
        except:
            pass

    def repeat_recording(self, speechReader, uiThread):
        while True:
            self.voice_lock.acquire()
            self.release_voice_lock()
            audio = speechReader.read_from_microphone(uiThread, timeout=2, phrase_time_limit=None)

            if audio is None:
                continue

            # don't do the rest when locked.
            if self.hotwordRecognizer is not None and self.hotwordRecognizer.isAlive():
                continue
            
            self.print_feedback_two("", uiThread)
            
            self.audio_count_semaphore.acquire()
            self.audio_count += 1
            self.print_feedback_three("Audio waiting for processing : " + str(self.audio_count), uiThread)
            self.audio_count_semaphore.release()

            self.buffer_semaphore.acquire()
            self.buffer.append(audio)
            try:
                self.buffer_semaphore.release()
            except:
                self.logger.log("buffer semaphore released without acquire @ repeat_recording")
            
        

    def main(self, uiThread):
        to_continue_reading = True
        self.uiThread = uiThread
        
        speechReader = SpeechReader()
        wordParser = newWordParser()
        fileReader = TextFileReader(self.text_filename)

        if self.read_from == CodingByDictationLogic.READ_FROM_SPEECH:
            # Repeatedly records voice on another thread.
            recording_thread = Thread(target = self.repeat_recording, args = (speechReader, uiThread,))
            recording_thread.start()
        
        while to_continue_reading:
            variables_list = self.build_var_list_from_stack(self.variables_stack)
            if "x" in variables_list:
                self.print_feedback_one("Error : 'x' is not an allowed variable, initiating undo...", uiThread)
                self.undo(True)
                continue
            
            # Speech to text
            read_audio = ""
            read_words = ""

            # Read from speech (voice)
            if self.read_from == CodingByDictationLogic.READ_FROM_SPEECH:
                while True:
                    self.buffer_semaphore.acquire()
                    if len(self.buffer) == 0:
                        read_audio = ""
                    else:
                        read_audio = self.buffer.pop(0)
                    try:
                        self.buffer_semaphore.release()
                    except:
                        self.logger.log("buffer semaphore released without acquire @ main")

                    # if listener program has not populate audio to buffer.
                    if (read_audio is ""):
                        pass
                    # something is read.
                    else:
                        read_words = speechReader.decipher_audio_with_api(read_audio, variables_list, uiThread, \
                                                                          self.api_used)
                        break
            # Read from audio file (pre-recorded file)
            elif self.read_from == CodingByDictationLogic.READ_FROM_AUDIO_FILE:
                read_audio = speechReader.read_from_audio_file(uiThread)
                read_words = speechReader.decipher_audio_with_api(read_audio, variables_list, uiThread, self.api_used)
            # Read from typing
            elif self.read_from == CodingByDictationLogic.READ_FROM_TYPING:
                read_words = raw_input("Type in speech : ")
            # Read from text file
            elif self.read_from == CodingByDictationLogic.READ_FROM_TEXT_FILE:
                read_words = fileReader.read_line()
                if read_words == "": # EOF
                    to_continue_reading = False
                    return
            else:
                print ("Error read_from in logic.py")
                return
                
            if read_words is None:
                # could not understand audio / user stop speaking.
                self.lock_voice(uiThread)
                continue

            if self.read_from == CodingByDictationLogic.READ_FROM_SPEECH:
                self.audio_count_semaphore.acquire()
                self.audio_count -= 1
                self.print_feedback_three("Audio waiting for processing : " + str(self.audio_count), uiThread)
                self.audio_count_semaphore.release()

            if self.to_show_time:
                start_time = time.time()

            # text to processed_text
            wordCorrector = WordCorrector(read_words, variables_list, self.create_func_complete.peek())
            corrected = wordCorrector.run_correction()

            if self.to_show_time:
                checkpoint1 = time.time()
                print ("Time to word correction = " + str(checkpoint1 - start_time))

            num_undo = corrected.strip().count("undo")

            if num_undo > 0:
                for i in range(num_undo):
                    self.undo(True)
                continue
            elif "clear" in corrected:
                self.clear()
                continue

            if "not recording" in corrected or "start recording" in read_words:
                continue

            # processed_text to structured_command / code and display to user.
            text_to_parse = self.build_string_from_stack(self.text_history_stack, self.accepted_indices) + " " + str(corrected)

            error_message = ""
            potential_missing = ""
            structured_command = ""

            try:
                temp_parse_struct = wordParser.parse(text_to_parse, True)
            except Exception as ex:
                self.print_feedback_four("Unable to understand : " + str(corrected), uiThread)
                self.lock_voice(uiThread)
                continue

            if self.to_show_time:
                checkpoint2 = time.time()
                print ("Time to parse word = " + str(checkpoint2 - checkpoint1))

            # Deep copy object over, else it will be overwritten (this is some weird bug.)
            result_structure = copy.deepcopy(temp_parse_struct)

            if self.to_show_time:
                checkpoint3 = time.time()
                print ("Time to deep copy structure = " + str(checkpoint3- checkpoint2))

            for i in range(0, len(result_structure["sentence_status"])):                
                if result_structure["sentence_status"][i]: # sentence can be parsed.
                    variable_current = result_structure["variables"][i]
                    parsed = result_structure["parsed"][i]

                    self.variables_stack.push(variable_current)
                    self.create_func_complete.push(result_structure["func_dec_complete"][i])

                    if len(result_structure["text"][i]) < len(str(corrected)):
                        self.text_history_stack.push(result_structure["text"][i])
                    else:
                        self.text_history_stack.push(str(corrected))

                    self.accepted_indices.append(self.current_index)
                    self.print_code(False, parsed, wordParser, uiThread)

                    self.current_index += 1
                else: # sentence cannot be parsed.                    
                    error_message = result_structure["expected"]
                    potential_missing = result_structure["potential_missing"]
                    variable_current = result_structure["variables"][i]
                    parsed = result_structure["parsed"][i]
                    
                    self.variables_stack.push(variable_current)
                    self.create_func_complete.push(result_structure["func_dec_complete"][i])
                    
                    if len(result_structure["text"][i]) < len(str(corrected)):
                        self.text_history_stack.push(result_structure["text"][i])
                    else:
                        # need to append end equal to avoid bug where prev sentence ends with var name,
                        # and subsequent sentence is another var assignment (begins with var name)
                        # It is then hard to decipher which var name belongs to which sentence.
                        if wordParser.need_to_append_end_equal(str(corrected)):
                            corrected = str(corrected) + " end equal"
                        self.text_history_stack.push(str(corrected))
                    self.print_code(True, parsed, wordParser, uiThread)

                    self.current_index += 1

            if self.to_show_time:
                checkpoint4 = time.time()
                print ("Time to iterate sentences in structure = " + str(checkpoint4 - checkpoint3))

            # Feedback to user
            if error_message != "" or self.error_from_scparser: # there is error message
                if self.error_from_scparser:
                    pass # error message shown at print_code function
                elif potential_missing != "":
                    self.print_feedback_one("Expected  : " + potential_missing, uiThread)
                else:
                    if error_message.strip() == "Expected":
                        self.print_feedback_one("Incomplete statement.", uiThread)
                    else:
                        self.print_feedback_one("Error     : " + error_message, uiThread)
            else:
                self.print_feedback_one(" ", uiThread)

            if self.to_show_time:
                checkpoint5 = time.time()
                print ("Time to parse word = " + str(checkpoint5 - checkpoint4))

            # printlines for debug
            print "Audio read by Speech Recognizer : " + read_words
            print "Processed text after correction : " + corrected
            self.logger.log(read_words + " --> " + corrected)

            if self.to_show_time:
                checkpoint6 = time.time()
                print ("Time to print console and log = " + str(checkpoint6 - checkpoint5))

            self.print_feedback_four("Read: " + corrected, uiThread)
            
            self.print_history_text(uiThread)
            # self.print_all_var() # for debug only.

            if self.to_show_time:
                checkpoint7 = time.time()
                print ("Time to update UI = " + str(checkpoint7 - checkpoint6))

