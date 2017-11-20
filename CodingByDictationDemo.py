import os
import speechrecogniser as SpeechReader
from WordCorrector import WordCorrector
from NewWordParser import WordParser as newWordParser
import StructuralCommandParser as scParser
from TextFileReader import TextFileReader

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
api_used = GOOGLE_CLOUD
text_filename = "FindMaximum.txt" # default is "FindMaximum.txt"


def print_equal(num_times):
    equal_str = ""
    for i in range(num_times):
        equal_str += "="
        
    print equal_str


def print_header_text(header_text, div_len_to_append = 0):
    num_words = len(header_text)
    print_equal(num_words + div_len_to_append)
    print header_text
    print_equal(num_words + div_len_to_append)
    

def print_all_accepted_text(accepted_text, additional_text_if_any = None):
    if len(accepted_text) == 0:
        if additional_text_if_any is None or additional_text_if_any == "":
            print "<<< No accepted text yet. >>>"
        else:
            print additional_text_if_any
    else:
        for text in accepted_text:
            print text
        if additional_text_if_any is not None and additional_text_if_any != "":
            print additional_text_if_any


def print_newlines(num_newlines = 1):
    for i in range(num_newlines):
        print "\n"

def get_struct_command_from_text_list(wordParser, text_list):
    struct_command_list = []
    
    for text in text_list:
        structured_command = wordParser.parse(text, False)
        struct_command_list.append(structured_command)
    return " ".join(struct_command_list)

def add_var_list(temp_variable_list, variables_list):
    temp_set = set()
    merged_list = temp_variable_list + variables_list
    for item in merged_list:
        temp_set.add(item)

    return list(temp_set)     

def main():
    to_continue_reading = True
    previous_text = ""
    previous_sample_code = ""
    variables_list = []
    accepted_text = []
    wordParser = newWordParser()
    fileReader = TextFileReader(text_filename)
    
    while to_continue_reading:
        temp_variable_list = [] # reset the var list
        
        # Speech to text
        if read_from == READ_FROM_SPEECH:
            read_words = SpeechReader.get_voice_input(variables_list, api_used, VOICE)
        elif read_from == READ_FROM_AUDIO_FILE:
            read_words = SpeechReader.get_voice_input(variables_list, api_used, AUDIO_FILE)
        elif read_from == READ_FROM_TYPING:
            read_words = raw_input("Type in speech : ")
        elif read_from == READ_FROM_TEXT_FILE:
            read_words = fileReader.read_line()
            if read_words == "": # EOF
                to_continue_reading = False
                
        else:
            print "Error: unknown read_from detected"
            return None # terminate the program

        if (read_words is None):
            print "Invalid input when reading"
            continue

        # text to processed_text
        wordCorrector = WordCorrector(read_words, variables_list)
        corrected = wordCorrector.run_correct_words_multiple("")
        corrected = wordCorrector.run_correct_variables()

        # processed_text to structured_command / code and display to user.
        text_to_parse = str(previous_text) + " " + str(corrected)

        error_message = ""
        potential_missing = ""
        structured_command = wordParser.parse(text_to_parse, False)
        if structured_command == "": # cannot parse
            result_struct = wordParser.parse_with_correction(text_to_parse)

            if "expected" in result_struct.keys():
                error_message = result_struct["expected"]
            if "potential_missing" in result_struct.keys():
                potential_missing = result_struct["potential_missing"]
            if "variables" in result_struct.keys() and len(result_struct["variables"]) != 0:
                temp_variable_list = result_struct["variables"]

            parsed = result_struct["parsed"]
        else: # can parse
            parsed = structured_command
            temp_variable_list = wordParser.get_variables()

        accepted_struct_commands = get_struct_command_from_text_list(wordParser, accepted_text)
        parsed = accepted_struct_commands + " " + parsed
        
        sample_code = scParser.parse_structural_command_to_code(parsed)

        # Feedback to user
        print_header_text("==========================================", 0)
        print_newlines()
        print_header_text("Sentences entered to date : ", 10)
        print_all_accepted_text(accepted_text, text_to_parse)
        if error_message == "":
            print_newlines()
            print_header_text(" Generated Code fragment:", 2)
            print sample_code
        else:
            print_newlines()
            print_header_text("Potential Code fragment:", 0)
            print sample_code
            print_newlines()
            print_header_text("Feedback", 15)
            if potential_missing != "":
                print "Expected  : " + potential_missing
            else:
                if error_message.strip() == "Expected":
                    print "Incomplete statement."
                else:
                    print "Error     : " + error_message
            print_newlines()

        print_header_text("Current Context", 45)
        print "Audio read by Speech Recognizer : " + read_words
        print "Processed text after correction : " + corrected
        print_newlines()

        if read_from == READ_FROM_TEXT_FILE:
            if to_continue_reading == True:
                input_continue = "y"
            else:
                input_continue = "d"
        else:
            input_continue = raw_input("\nType 'y' to accept and continue, 'n' to reject and continue, 'd' to accept and stop, " + \
                               "'t' to reject and stop. \n")

        is_rejected = True   
        if input_continue.lower() == "y":
            # Accept and continue
            to_continue_reading = True
            is_rejected = False
            
            if error_message == "":
                accepted_text.append(text_to_parse)
                previous_text = ""
                variables_list = add_var_list(temp_variable_list, variables_list)
            else: # incomplete
                previous_text = text_to_parse
        elif input_continue.lower() == "n":
            # Reject and continue
            to_continue_reading = True
        elif input_continue.lower() == "d":
            # Accept and stop
            to_continue_reading = False
            is_rejected = False

            if error_message == "":
                accepted_text.append(text_to_parse)
                previous_text = ""
                variables_list = add_var_list(temp_variable_list, variables_list)
            else: # incomplete
                previous_text = text_to_parse
        elif input_continue.lower() == "t":
            # Reject and stop
            to_continue_reading = False
        else:
            to_continue_reading = False # else reject and stop

        if to_continue_reading:
            print_newlines(2)
            print_header_text("Accepted sentences entered to date : ", 2)
            print_all_accepted_text(accepted_text, "")
            print_newlines()
            print_header_text("Pending sentences : ", 20)
            if previous_text == "":
                print "<<< No pending text yet. >>>"
            else:
                print previous_text
            print_newlines()
            print_header_text("Code fragment : ", 20)
            if is_rejected:
                print previous_sample_code
            else:
                print sample_code
                previous_sample_code = sample_code
            print "====================================="
            print_newlines()
        

    # convert word to structured command
    accepted_struct_commands = get_struct_command_from_text_list(wordParser, accepted_text)

    # Convert structured command to code
    code = scParser.parse_structural_command_to_code(accepted_struct_commands)

    # Output final code
    print code
    
# Run the main function
main()

