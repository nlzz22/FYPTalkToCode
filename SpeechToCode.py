import os
import speechrecogniser as SpeechReader
from WordParser import WordParser
import StructuralCommandParser as scParser


def main():
    # Read from audio and process to words
    read_words = SpeechReader.get_voice_input()
    if (read_words is None):
        print "Invalid input when reading from audio"
        return

    print "Audio deciphered : " + read_words + "\n"

    # Convert words to structured command
    wordParser = WordParser(read_words)
    structured_command = wordParser.map_word_to_structured_command()

    # Convert structured command to code
    code = scParser.parse_structural_command_to_code(structured_command)

    # Output final code
    print code
    
# Run the main function
main()
