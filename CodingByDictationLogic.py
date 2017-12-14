import os
import wx
from SpeechRecogniser import SpeechRecognitionModule as SpeechReader
from WordCorrector import WordCorrector
from NewWordParser import WordParser as newWordParser
from NewWordParser import Stack
import StructuralCommandParser as scParser
from TextFileReader import TextFileReader
import time

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

# EDIT THIS ONLY.
# User defined: Method of reading here.
read_from = READ_FROM_SPEECH
api_used = GOOGLE
text_filename = "FindMaximum.txt" # default is "FindMaximum.txt"  

def print_history_text(text_hist_stack, accepted_indices, uiThread):
    hist_text = ""
    curr_index = 0
    for i in range(0, len(text_hist_stack.stack)):
        if curr_index < len(accepted_indices) and i == accepted_indices[curr_index]:
            hist_text += text_hist_stack.stack[i] + "\n"
            curr_index += 1
        else:
            hist_text += text_hist_stack.stack[i] + " "   
    
    uiThread.UpdateHistoryBody(hist_text)

def print_code(text_hist_stack, accepted_indices, to_add_corrected, parsed_sc, wordParser, scParser, uiThread):
    accepted_text_list = []
    curr_text = ""
    curr_index = 0
    for i in range(0, len(text_hist_stack.stack)):
        if curr_index < len(accepted_indices) and i == accepted_indices[curr_index]:
            curr_text += text_hist_stack.stack[i] + " "
            curr_index += 1
            accepted_text_list.append(curr_text)
            curr_text = ""
        else:
            curr_text += text_hist_stack.stack[i] + " "

    structured_command = get_struct_command_from_text_list(wordParser, accepted_text_list)
    if to_add_corrected:
        structured_command += " " + parsed_sc
    code = scParser.parse_structural_command_to_code(structured_command)
  
    uiThread.UpdateCodeBody(code)

def print_feedback_one(feedback, uiThread):
    uiThread.UpdateFeedbackOne(feedback)

def print_feedback_two(feedback, uiThread):
    uiThread.UpdateFeedbackTwo(feedback)

def print_feedback_three(feedback, uiThread):
    uiThread.UpdateFeedbackThree(feedback)

def get_struct_command_from_text_list(wordParser, text_list):
    struct_command_list = []
    
    for text in text_list:
        structured_command = wordParser.parse(text, False)
        struct_command_list.append(structured_command)
    return " ".join(struct_command_list)

def build_var_list_from_stack(stackClass):
    temp_set = set()
    for curr_var_list in stackClass.stack:
        for variable in curr_var_list:
            temp_set.add(variable)

    return list(temp_set)

def build_string_from_stack(stackClass, accepted_indices):
    joined_string = ""
    if len(accepted_indices) == 0:
        last_accepted_index = -1
    else:
        last_accepted_index = accepted_indices[len(accepted_indices) - 1]

    for i in range(last_accepted_index + 1, len(stackClass.stack)):
        joined_string += stackClass.stack[i] + " "
    return joined_string    

def main(uiThread):
    to_continue_reading = True
    variables_stack = Stack()
    text_history_stack = Stack()
    accepted_indices = []
    current_index = 0
    speechReader = SpeechReader()
    wordParser = newWordParser()
    fileReader = TextFileReader(text_filename)
    
    while to_continue_reading:
        variables_list = build_var_list_from_stack(variables_stack)
        
        # Speech to text
        if read_from == READ_FROM_SPEECH:
            read_words = speechReader.get_voice_input(variables_list, api_used, VOICE, uiThread)
        elif read_from == READ_FROM_AUDIO_FILE:
            read_words = speechReader.get_voice_input(variables_list, api_used, AUDIO_FILE, uiThread)
        elif read_from == READ_FROM_TYPING:
            read_words = raw_input("Type in speech : ")
        elif read_from == READ_FROM_TEXT_FILE:
            read_words = fileReader.read_line()
            if read_words == "": # EOF
                to_continue_reading = False
                
        else:
            print_feedback_one("Error: unknown read_from detected", uiThread)
            return None # terminate the program

        if (read_words is None):
            print_feedback_one("Invalid input when reading", uiThread)
            time.sleep(2)
            continue

        # text to processed_text
        wordCorrector = WordCorrector(read_words, variables_list)
        corrected = wordCorrector.run_correct_words_multiple("")
        corrected = wordCorrector.run_correct_variables()

        # processed_text to structured_command / code and display to user.
        text_to_parse = build_string_from_stack(text_history_stack, accepted_indices) + " " + str(corrected)

        error_message = ""
        potential_missing = ""
        structured_command = wordParser.parse(text_to_parse, False)

        to_add_corrected = False
        if structured_command == "": # cannot parse
            result_struct = wordParser.parse_with_correction(text_to_parse)

            if "expected" in result_struct.keys():
                error_message = result_struct["expected"]
            if "potential_missing" in result_struct.keys():
                potential_missing = result_struct["potential_missing"]
            if "variables" in result_struct.keys() and len(result_struct["variables"]) != 0:
                variables_stack.push(result_struct["variables"])
            else:
                variables_stack.push([])

            to_add_corrected = True
            parsed = result_struct["parsed"]
        else: # can parse
            parsed = structured_command
            variables_stack.push(wordParser.get_variables())
            accepted_indices.append(current_index)
       
        sample_code = scParser.parse_structural_command_to_code(parsed)

        # Feedback to user
        if error_message != "":
            if potential_missing != "":
                print_feedback_two("Expected  : " + potential_missing, uiThread)
            else:
                if error_message.strip() == "Expected":
                    print_feedback_two("Incomplete statement.", uiThread)
                else:
                    print_feedback_two("Error     : " + error_message, uiThread)
        else:
            print_feedback_two(" ", uiThread)

        # printlines for debug
        print "Audio read by Speech Recognizer : " + read_words
        print "Processed text after correction : " + corrected

        print_feedback_three("Read: " + corrected, uiThread)

        if read_from == READ_FROM_TEXT_FILE:
            if to_continue_reading == True:
                input_continue = "y"
            else:
                input_continue = "d"
        else:
            input_continue = "y"
        
        if input_continue.lower() == "y":
            # Accept and continue
            to_continue_reading = True
            current_index += 1

            text_history_stack.push(str(corrected))
        elif input_continue.lower() == "d":
            # Accept and stop
            to_continue_reading = False

            text_history_stack.push(str(corrected))
        else:
            to_continue_reading = False # else reject and stop

        print_history_text(text_history_stack, accepted_indices, uiThread)
        print_code(text_history_stack, accepted_indices, to_add_corrected, parsed, wordParser, scParser, uiThread)

