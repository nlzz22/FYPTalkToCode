import os
import speechrecogniser as SpeechReader
from WordCorrector import WordCorrector
from NewWordParser import WordParser as newWordParser
import StructuralCommandParser as scParser

def get_parsable_portion(original_text, unparsed_text):
    try:
        index = original_text.index(unparsed_text)

        actual_inverted_index = len(unparsed_text)
        parsable_portion = original_text[:len(original_text) - actual_inverted_index]

        return parsable_portion
    except ValueError: # not found
        return None

def main():
    to_continue_reading = True
    struct_cmd_builder = []
    sentences = []
    unparsed_text = ""
    #prev_unparsed_text = ""
    wordParser = newWordParser()
    
    while to_continue_reading:
        # Speech to text
        read_words = SpeechReader.get_voice_input()
        if (read_words is None):
            print "Invalid input when reading from audio"
            continue

        # text to processed_text
        wordCorrector = WordCorrector(read_words)
        corrected = wordCorrector.run_correct_words_multiple("")

        # processed_text to structured_command
        text_to_parse = ""
        
        if unparsed_text is not None and unparsed_text != "":
            text_to_parse = str(unparsed_text) + " " + str(corrected)
        else:
            text_to_parse = str(corrected)

        structured_command = wordParser.parse(str(text_to_parse))
        current_unparsed_text = wordParser.retrieve_additional_unparsed()
        
        parsed_text = get_parsable_portion(text_to_parse, current_unparsed_text) 

        print "=========================================="
        print "Text already entered: "
        print "\n".join(sentences)
        print "=========================================="
        print "*** Current Context *** "
        print "Text that can be parsed    : " + parsed_text
        print "Text that cannot be parsed : " + current_unparsed_text
        print "=========================================="
        print "Audio read : " + read_words
        print "Corrected text : " + corrected
        print "\n"
        

        input_continue = raw_input("\nType 'y' to accept and continue, 'n' to reject and continue, 'd' to accept and stop, " + \
                                   "'t' to reject and stop. \n")
        if input_continue.lower() == "y":
            # Accept and continue
            to_continue_reading = True
            struct_cmd_builder.append(structured_command)
            if parsed_text != "":
                sentences.append(parsed_text)
            unparsed_text = current_unparsed_text
        elif input_continue.lower() == "n":
            # Reject and continue
            to_continue_reading = True
        elif input_continue.lower() == "d":
            # Accept and stop
            to_continue_reading = False
            struct_cmd_builder.append(structured_command)
            if parsed_text != "":
                sentences.append(parsed_text)
            unparsed_text = current_unparsed_text
        elif input_continue.lower() == "t":
            # Reject and stop
            to_continue_reading = False
        else:
            to_continue_reading = False # else reject and stop
            
    # join all structured_command together to await parsing to code
    final_struct_command = " ".join(struct_cmd_builder)
    print "Final structured command : " + final_struct_command

    # Convert structured command to code
    code = scParser.parse_structural_command_to_code(final_struct_command)

    # Output final code
    print code
    
# Run the main function
main()

