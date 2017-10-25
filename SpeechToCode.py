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
read_from = READ_FROM_TYPING
api_used = GOOGLE
text_filename = "FindMaximum.txt" # default is "FindMaximum.txt"

def get_struct_command_from_text_list(wordParser, text_list):
    struct_command_list = []
    
    for text in text_list:
        structured_command = wordParser.parse(text)
        struct_command_list.append(structured_command)
    return " ".join(struct_command_list)

def main():
    to_continue_reading = True
    previous_text = ""
    variables_list = []
    accepted_text = []
    wordParser = newWordParser()
    fileReader = TextFileReader(text_filename)
    
    while to_continue_reading:
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
        structured_command = wordParser.parse(text_to_parse)
        if structured_command == "": # cannot parse
            result_struct = wordParser.parse_with_correction(text_to_parse)

            if "expected" in result_struct.keys():
                error_message = result_struct["expected"]
            if "potential_missing" in result_struct.keys():
                potential_missing = result_struct["potential_missing"]
            if "variables" in result_struct.keys() and len(result_struct["variables"]) != 0:
                variables_list = result_struct["variables"]

            parsed = result_struct["parsed"]
        else: # can parse
            parsed = structured_command
            variables_list = wordParser.get_variables()

        accepted_struct_commands = get_struct_command_from_text_list(wordParser, accepted_text)
        parsed = accepted_struct_commands + " " + parsed
        
        sample_code = scParser.parse_structural_command_to_code(parsed)

        print "=========================================="
        print "\n"
        print "Sentences to date : "
        print "===================="
        for text in accepted_text:
            print text
        print text_to_parse
        if error_message == "":
            print "\n"
            print " Code fragment:"
            print "================"
            print sample_code
        else:
            print "\n"
            print "Potential code fragment"
            print "======================="
            print sample_code
            print "\n"
            if potential_missing != "":
                print "Expected  : " + potential_missing
            else:
                if error_message.strip() == "Expected":
                    print "Incomplete statement."
                else:
                    print "Error     : " + error_message
            print "\n"

        print "=========================================="
        print "Audio read : " + read_words
        print "Corrected text : " + corrected
        print "\n"

        if read_from == READ_FROM_TEXT_FILE:
            if to_continue_reading == True:
                input_continue = "y"
            else:
                input_continue = "d"
        else:
            input_continue = raw_input("\nType 'y' to accept and continue, 'n' to reject and continue, 'd' to accept and stop, " + \
                               "'t' to reject and stop. \n")

            
        if input_continue.lower() == "y":
            # Accept and continue
            to_continue_reading = True
            
            if error_message == "":
                accepted_text.append(text_to_parse)
                previous_text = ""
            else: # incomplete
                previous_text = text_to_parse
        elif input_continue.lower() == "n":
            # Reject and continue
            to_continue_reading = True
        elif input_continue.lower() == "d":
            # Accept and stop
            to_continue_reading = False

            if error_message == "":
                accepted_text.append(text_to_parse)
                previous_text = ""
            else: # incomplete
                previous_text = text_to_parse
        elif input_continue.lower() == "t":
            # Reject and stop
            to_continue_reading = False
        else:
            to_continue_reading = False # else reject and stop

    # convert word to structured command
    accepted_struct_commands = get_struct_command_from_text_list(wordParser, accepted_text)

    # Convert structured command to code
    code = scParser.parse_structural_command_to_code(accepted_struct_commands)

    # Output final code
    print code
    
# Run the main function
main()

