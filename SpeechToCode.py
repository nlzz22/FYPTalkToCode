import os
import speechrecogniser as SpeechReader
from WordCorrector import WordCorrector
from NewWordParser import WordParser as newWordParser
import StructuralCommandParser as scParser

def main():
    to_continue_reading = True
    previous_text = ""
    variables_list = []
    wordParser = newWordParser()
    
    while to_continue_reading:
        # Speech to text
        read_words = SpeechReader.get_voice_input(variables_list)
        #read_words = raw_input("Type in speech : ")
        if (read_words is None):
            print "Invalid input when reading from audio"
            continue

        # text to processed_text
        wordCorrector = WordCorrector(read_words)
        corrected = wordCorrector.run_correct_words_multiple("")

        # processed_text to structured_command / code and display to user.
        text_to_parse = str(previous_text) + "\n" + str(corrected)

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

        sample_code = scParser.parse_structural_command_to_code(parsed)

        print "=========================================="
        print "\n"
        print "Sentences to date : "
        print "===================="
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

        input_continue = raw_input("\nType 'y' to accept and continue, 'n' to reject and continue, 'd' to accept and stop, " + \
                                   "'t' to reject and stop. \n")
        if input_continue.lower() == "y":
            # Accept and continue
            to_continue_reading = True
            previous_text = text_to_parse
        elif input_continue.lower() == "n":
            # Reject and continue
            to_continue_reading = True
        elif input_continue.lower() == "d":
            # Accept and stop
            to_continue_reading = False
            previous_text = text_to_parse
        elif input_continue.lower() == "t":
            # Reject and stop
            to_continue_reading = False
        else:
            to_continue_reading = False # else reject and stop

    # convert word to structured command
    structured_command = wordParser.parse(previous_text)

    # Convert structured command to code
    code = scParser.parse_structural_command_to_code(structured_command)

    # Output final code
    print code
    
# Run the main function
main()

