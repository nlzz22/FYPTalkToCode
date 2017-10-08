import os
import speechrecogniser as SpeechReader
from WordCorrector import WordCorrector
from WordParser import WordParser
from NewWordParser import WordParser as newWordParser
import StructuralCommandParser as scParser


def main():
    to_continue_reading = True
    sentences = []
    
    # Read from audio and process to words
    while to_continue_reading:
        read_words = SpeechReader.get_voice_input()
        if (read_words is None):
            print "Invalid input when reading from audio"
            return

        print "Audio deciphered : " + read_words + "\n"
        sentences.append(read_words)

        input_continue = raw_input("Continue recording ? (Type 'Y' to continue)\n")
        if input_continue.lower() != "y":
            to_continue_reading = False

    # join all words together to a complete sentence
    words = " ".join(sentences)
    print words

    # Correct words
    wordCorrector = WordCorrector(words)
    corrected = wordCorrector.run_correct_words_multiple("")
 
    # Convert words to structured command
    #wordParser = WordParser(corrected)
    #structured_command = wordParser.map_word_to_structured_command()
    wordParser = newWordParser()
    structured_command = wordParser.parse(str(corrected))

    # Convert structured command to code
    code = scParser.parse_structural_command_to_code(structured_command)

    # Output final code
    print code
    
# Run the main function
main()
