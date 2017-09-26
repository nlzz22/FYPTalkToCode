from WordParser import WordParser
import StructuralCommandParser

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
print code
