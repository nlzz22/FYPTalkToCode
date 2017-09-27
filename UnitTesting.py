import unittest
from WordParser import WordParser
from WordCorrector import WordCorrector
import StructuralCommandParser

class TestParserMethods(unittest.TestCase):
    def test_word_and_struct_command_parser(self):
        word = "create function find maximum with return type integer with parameter integer array numbers "
        word += "with parameter integer length begin "
        word += "declare integer max equal numbers array index zero end declare declare integer i end declare "
        word += "for loop condition i equal one condition i less than length condition i plus plus begin "
        word += "if numbers array index i greater than max then "
        word += "max equal numbers array index i end equal "
        word += "end if "
        word += "end for loop "
        word += "return max "
        word += " end function "

        wordParser = WordParser(word)
        structCommand = wordParser.map_word_to_structured_command()

        code = StructuralCommandParser.parse_structural_command_to_code(structCommand)
        req_code = "#include <stdio.h> int findMaximum(int [], int ); int findMaximum(int numbers[], int length){ int max = numbers[0]; int i; for (i = 1;i < length;i++){ if(numbers[i] > max) { max = numbers[i]; } } return max; }"

        self.assertEqual(self.format_spaces(code), self.format_spaces(req_code))

    def test_word_corrector_one_use(self):
        words = "create function find Maximum Reef return type integer with parameter integer array numbers"
        words += " with parameter integer length begin declare in the jail max equal numbers array index 0 end declare"
        words += " declare integer i end declare 4 loop condition i equal one condition i less than length condition i plus plus begin"
        words += " if numbers array index i greater than Max"
        words += " then max equal numbers array Intex i end equal end if end for loop return Max and function"
        wordCorrector = WordCorrector(words)
        corrected = wordCorrector.correct_words()
        req_words = "create function find maximum with return type integer with parameter integer array numbers with parameter integer length begin "
        req_words += "declare integer max equal numbers array index zero end declare "
        req_words += "declare integer i end declare "
        req_words += "for loop condition i equal one condition i less than length condition i plus plus begin "
        req_words += "if numbers array index i greater than max then "
        req_words += "max equal numbers array index i end equal "
        req_words += "end if end for loop return max end function "

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(req_words))

    def test_word_corrector_multiple_use(self):
        words = "4 loop condition eye equal 1 if numbers away intex i"
        req_words = "for loop condition i equal one if numbers array index i"

        wordCorrector = WordCorrector(words)
        corrected = wordCorrector.run_correct_words_multiple()

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(req_words))

    def test_word_parser_with_correction(self):
        word = "create function find maximum reef written type integer with parameter integer array numbers "
        word += "with parameter integer length begin "
        word += "declare integer max equal numbers away intex zero end declare declare integer i end declare "
        word += "for loop condition i equal one condition i less than length condition eye plus plus begin "
        word += "if numbers array index i greater than max then "
        word += "max equal numbers array index i and equal "
        word += "end if "
        word += "and for loop "
        word += "return max "
        word += " end function "

        wordParser = WordParser(word)
        structCommand = wordParser.map_word_to_structured_command()

        code = StructuralCommandParser.parse_structural_command_to_code(structCommand)
        req_code = "#include <stdio.h> int findMaximum(int [], int ); int findMaximum(int numbers[], int length){ int max = numbers[0]; int i; for (i = 1;i < length;i++){ if(numbers[i] > max) { max = numbers[i]; } } return max; }"

        self.assertEqual(self.format_spaces(code), self.format_spaces(req_code))

    def test_actual_from_word_to_code(self):
        word = "create function find maximum width return type integer with parameter integer array numbers "
        word += "with parameter integer length begin declare integer Max equal numbers array index 0 end declare "
        word += "declare integer I end declare "
        word += "for Loop condition is equal one condition I less than length condition I plus plus begin "
        word += "if numbers array index I greater than Max Den Max equal numbers array index I and equal and if and for Loop return Max "
        word += "and function"

        wordParser = WordParser(word)
        structCommand = wordParser.map_word_to_structured_command()

        code = StructuralCommandParser.parse_structural_command_to_code(structCommand)
        req_code = "#include <stdio.h> int findMaximum(int [], int ); int findMaximum(int numbers[], int length){ int max = numbers[0]; int i; for (i = 1;i < length;i++){ if(numbers[i] > max) { max = numbers[i]; } } return max; }"

        self.assertEqual(self.format_spaces(code), self.format_spaces(req_code))

    def format_spaces(self, sentence):
        return ' '.join(sentence.split())
        

if __name__ == '__main__':
    unittest.main()
