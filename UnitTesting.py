import unittest
from NewWordParser import WordParser
from WordCorrector import WordCorrector
import WordSimilarity
import StructuralCommandParser

class TestParserMethods(unittest.TestCase):
    # Test word corrector
    def test_word_corrector_variables(self):
        word = "eye equal one end equal "
        word += "next equal two end equal"
        wc = WordCorrector(word, ["max", "i"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "i equal one end equal max equal two end equal"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))


    def test_word_corrector_variables_not_found(self):
        word = "length equal thirty end equal"
        wc = WordCorrector(word, ["max", "i"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = word # no correction as "length" is not similar to either "max" or "i"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))


    def test_word_corrector_variables_escape_words_declare(self):
        word = "declare integer eye end declare"
        wc = WordCorrector(word, ["max", "i"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = word # no correction as word starts with escape word "declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_variables_escape_words_create_func(self):
        word = "create function find maximum with return type integer begin end function"
        wc = WordCorrector(word, ["max", "bind", "mind"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = word # no correction as word starts with escape word "create function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_variables_string_literal(self):
        word = "call function find parameter string next end string end function"
        wc = WordCorrector(word, ["max", "mind"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "call function mind parameter string next end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_variables_character_literal(self):
        word = "max equal character a end declare"
        wc = WordCorrector(word, ["max", "eh", "aa"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = word
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_normal(self):
        word = "create function find maximum width return type integer with parameter integer array numbers \
         with parameter integer length begin declare integer Max equal numbers array index 0 end declare \
         declare integer I end declare \
         for Loop condition is equal one condition I less than length condition I plus plus begin \
         if numbers array index I greater than Max Den Max equal numbers array index I and equal and if and for Loop return Max \
         and function"
        wc = WordCorrector(word, ["max", "length", "i", "numbers"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "create function find maximum with return type integer with parameter integer array numbers \
            with parameter integer length begin declare integer max equal numbers array index zero end declare \
            declare integer i end declare for loop condition i equal one condition i less than length condition i plus plus begin \
            if numbers array index i greater than max then max equal numbers array index i end equal \
            end if end for loop return max end function"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_bug_with_four(self):
        word = "sequence array index three equal four end equal"
        wc = WordCorrector(word, [])
        corrected = wc.run_correct_words_multiple("")
        expected = word
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))


    def test_word_corrector_bug_with_no_whole_word_replace(self):
        word = "for loop condition i equal one"
        wc = WordCorrector(word, ["max"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "for loop condition max equal one"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_ii_to_i(self):
        word = "first equal II end equal"
        wc = WordCorrector(word, ["first", "i"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "first equal i end equal"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_ii_to_second(self):
        word = "first equal II end equal"
        wc = WordCorrector(word, ["first", "second"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "first equal second end equal"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_ii_to_none(self):
        word = "first equal II end equal"
        wc = WordCorrector(word, ["first"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = word.lower()
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_equal_to(self):
        word = "declare integer second equal to end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "declare integer second equal two end declare"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_do_not_correct_equal_to(self):
        word = "declare integer second equal to end declare"
        wc = WordCorrector(word, ["to"])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = "declare integer second equal to end declare"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_bug_declare_var_to(self):
        word = "declare integer to end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correct_words_multiple("")
        corrected = wc.run_correct_variables()
        expected = word
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))


    # Test word similarity

    def test_word_similarity_1(self):
        word = "eye"
        list_vars = ["i", "numbers", "max", "length"]
        expected = "i"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    def test_word_similarity_2(self):
        word = "lumber"
        list_vars = ["i", "numbers", "max", "length"]
        expected = "numbers"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    def test_word_similarity_3(self):
        word = "next"
        list_vars = ["i", "numbers", "max", "length"]
        expected = "max"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    def test_word_similarity_4(self):
        word = "lang"
        list_vars = ["i", "numbers", "max", "length"]
        expected = "length"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    def test_word_similarity_5(self):
        word = "blank"
        list_vars = ["i", "numbers", "max", "length"]
        expected = "length"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    def test_word_similarity_6(self):
        word = "makes"
        list_vars = ["i", "numbers", "max", "length"]
        expected = "max"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    # Test structured command parser

    def test_struct_command_parser(self):
        struct_command = "#function_declare findMaximum int #parameter_a #dimension 1 int #array numbers " + \
             "#parameter int length #function_start " + \
            "#create int #variable max #array numbers #indexes  #value 0 #index_end #dec_end;; " + \
            "#create int #variable i #dec_end;; " + \
            "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start " + \
            "if #condition #array  numbers #indexes  #variable  i #index_end > #variable max #if_branch_start " + \
            "#assign #variable max #with #array  numbers #indexes  #variable  i #index_end;; " + \
            "#if_branch_end;; #for_end;; return #variable max;; #function_end;;"
        converted_code = StructuralCommandParser.parse_structural_command_to_code(struct_command)
        expected_code = "#include <stdio.h> int findMaximum(int [], int ); int findMaximum(int numbers[], int length){ int max = numbers[0]; int i; for (i = 1;i < length;i++){ if(numbers[i] > max) { max = numbers[i]; } } return max; }"

        self.assertEqual(self.format_spaces(converted_code), self.format_spaces(expected_code))

    # Test word parser

    def test_word_parser_var_assign_equal_arr(self):
        speech = "max too equal numbers array index i end equal"
        struct = "#assign #variable maxToo #with #array numbers #indexes #variable i #index_end;;"
        self.wordparser_compare(speech, struct)

        speech = "max equal numbers hello array index two end equal"
        struct = "#assign #variable max #with #array numbersHello #indexes #value 2 #index_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_assign_number(self):
        speech = "max equal one hundred twenty two end equal"
        struct = "#assign #variable max #with #value 122;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_assign_var(self):
        speech = "max equal min end equal"
        struct = "#assign #variable max #with #variable min;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_array_index_var_assign_var(self):
        speech = "max tree array index i equal min end equal"
        struct = "#assign #array maxTree #indexes #variable i #index_end #with #variable min;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_array_index_number_assign_var(self):
        speech = "max array index twenty one equal min end equal"
        struct = "#assign #array max #indexes #value 21 #index_end #with #variable min;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_var_gt_var(self):
        speech = "begin if a greater than b then a equal b end equal c equal d end equal end if"
        struct = "if #condition #variable a > #variable b #if_branch_start #assign #variable a #with #variable b;; #assign #variable c #with #variable d;; #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_array_gt_var(self):
        speech = "begin if numbers array index i greater than max then end if"
        struct = "if #condition #array numbers #indexes #variable i #index_end > #variable max #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_array_lt_var(self):
        speech = "begin if numbers array index i less than max then end if"
        struct = "if #condition #array numbers #indexes #variable i #index_end < #variable max #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_array_gte_var(self):
        speech = "begin if numbers array index i greater than equal max then end if"
        struct = "if #condition #array numbers #indexes #variable i #index_end >= #variable max #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_array_lte_var(self):
        speech = "begin if numbers array index i less than equal max then end if"
        struct = "if #condition #array numbers #indexes #variable i #index_end <= #variable max #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_array_eq_var(self):
        speech = "begin if numbers array index i equal max then end if"
        struct = "if #condition #array numbers #indexes #variable i #index_end == #variable max #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_array_neq_var(self):
        speech = "begin if numbers array index i not equal max then end if"
        struct = "if #condition #array numbers #indexes #variable i #index_end != #variable max #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_else(self):
        # 1 if 1 else
        speech = "begin if max equal min then max equal one end equal else max equal two end equal end if"
        struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
        self.wordparser_compare(speech, struct)

        # 2 if 1 else
        speech = "begin if max equal min then max equal one end equal  a equal b end equal else max equal two end equal end if"
        struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #assign #variable a #with #variable b;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
        self.wordparser_compare(speech, struct)

        # 1 if 2 else
        speech = "begin if max equal min then max equal one end equal else a equal b end equal max equal two end equal end if"
        struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable a #with #variable b;; #assign #variable max #with #value 2;; #else_branch_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_var_else(self):
        speech = "begin if max then max equal one end equal else max equal two end equal end if"
        struct = "if #condition #variable max #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
        self.wordparser_compare(speech, struct)

        speech = "begin if max minus two then max equal one end equal else max equal two end equal end if"
        struct = "if #condition #variable max - #value 2 #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_var(self):
        speech = "begin if max minus two then end if"
        struct = "if #condition #variable max - #value 2 #if_branch_start #if_branch_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_var_mult_stmts(self):
        speech = "begin if max then a equal b end equal c equal d end equal end if"
        struct = "if #condition #variable max #if_branch_start #assign #variable a #with #variable b;; #assign #variable c #with #variable d;; #if_branch_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop(self):
        speech = "for loop condition i equal one condition i less than length condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_assign_equal_expression(self):
        speech = "max equal numbers array index i plus min plus twenty end equal"
        struct = "#assign #variable max #with #array numbers #indexes #variable i #index_end + #variable min + #value 20;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_with_expr(self):
        speech = "for loop condition i equal one condition i plus two less than length condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i + #value 2 < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_with_expr(self):
        speech = "begin if i plus j plus k greater than max then end if"
        struct = "if #condition #variable i + #variable j + #variable k > #variable max #if_branch_start #if_branch_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_var_equal_array(self):
        speech = "declare integer max equal numbers array index zero end declare "
        struct = "#create int #variable max #array numbers #indexes  #value 0 #index_end #dec_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_var(self):
        speech = "declare integer i end declare"
        struct = "#create int #variable i #dec_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_var_two_words(self):
        speech = "declare integer mountain fox end declare"
        struct = "#create int #variable mountainFox #dec_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_var_equal_expr(self):
        speech = "declare integer i equal j plus one end declare"
        struct = "#create int #variable i #variable j + #value 1 #dec_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_var_equal_expr_multiple_words(self):
        speech = "declare integer i equal tax rate plus thirty one plus flower end declare"
        struct = "#create int #variable i #variable taxRate + #value 31 + #variable flower #dec_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_arr_size_number(self):
        speech = "declare integer array sequence with size ten end declare"
        struct = "#create int #array #variable sequence #indexes #value 10 #index_end #dec_end;;"    
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_arr_two_words_size_number(self):
        speech = "declare integer array sequence now with size ten end declare"
        struct = "#create int #array #variable sequenceNow #indexes #value 10 #index_end #dec_end;;"    
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_arr_size_var_with(self):
        speech = "declare integer array sequence with size amount end declare"
        struct = "#create int #array #variable sequence #indexes #variable amount #index_end #dec_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_arr_size_var(self):
        speech = "declare integer array sequence size amount end declare"
        struct = "#create int #array #variable sequence #indexes #variable amount #index_end #dec_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_arr_size_var_two_words(self):
        speech = "declare integer array sequence size amount obtained end declare"
        struct = "#create int #array #variable sequence #indexes #variable amountObtained #index_end #dec_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_return_var(self):
        speech = "return max"
        struct = "return #variable max;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_return_number(self):
        speech = "return zero"
        struct = "return #value 0;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_return_expr(self):
        speech = "return i plus two"
        struct = "return #variable i + #value 2;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_create_function(self):
        speech = "create function find maximum with return type integer with parameter integer array numbers " + \
                 "with parameter integer length begin end function"
        struct = "#function_declare findMaximum int #parameter_a #dimension 1 int #array numbers #parameter int length #function_start #function_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_create_function_main(self):
        speech = "create function main with return type void begin end function"
        struct = "#function_declare main #function_start #function_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_stmts(self):
        speech = "for loop condition i equal one condition i less than length condition i plus plus begin " + \
                 "begin if numbers array index i greater than max then " + \
                 "max equal numbers array index i end equal " + \
                 "end if end for loop "
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ " + \
                 "#for_start if #condition #array numbers #indexes #variable i #index_end > #variable max #if_branch_start " + \
                 "#assign #variable max #with #array numbers #indexes #variable i #index_end;; #if_branch_end;; #for_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_sample_code(self):
        speech = "create function find maximum with return type integer with parameter integer array numbers " + \
                 "with parameter integer length begin " + \
                 "declare integer max equal numbers array index zero end declare " + \
                 "declare integer i end declare " + \
                 "for loop condition i equal one condition i less than length condition i plus plus begin " + \
                 "begin if numbers array index i greater than max then " + \
                 "max equal numbers array index i end equal " + \
                 "end if end for loop return max end function "
        struct = "#function_declare findMaximum int #parameter_a #dimension 1 int #array numbers " + \
                 "#parameter int length #function_start " + \
                "#create int #variable max #array numbers #indexes  #value 0 #index_end #dec_end;; " + \
                "#create int #variable i #dec_end;; " + \
                "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start " + \
                "if #condition #array  numbers #indexes  #variable  i #index_end > #variable max #if_branch_start " + \
                "#assign #variable max #with #array  numbers #indexes  #variable  i #index_end;; " + \
                "#if_branch_end;; #for_end;; return #variable max;; #function_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_empty_body(self):
        speech = "while value less than equal three begin end while"
        struct = "while #condition #variable value <= #value 3 #while_start #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_normal(self):
        speech = "while value less than equal three begin max equal one end equal end while"
        struct = "while #condition #variable value <= #value 3 #while_start #assign #variable max #with #value 1;; #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_expr(self):
        # expr <= num 
        speech = "while value plus two less than equal three begin end while"
        struct = "while #condition #variable value + #value 2 <= #value 3 #while_start #while_end;;"
        self.wordparser_compare(speech, struct)

        # expr <= expr
        speech = "while value plus two less than equal three plus max begin end while"
        struct = "while #condition #variable value + #value 2 <= #value 3 + #variable max #while_start #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_var(self):
        speech = "while is done begin end while"
        struct = "while #condition #variable isDone #while_start #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_func_with_params(self):
        speech = "call function abc with parameter arr with parameter test end function"
        struct = "#function abc(#parameter #variable arr #parameter #variable test);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_func_with_params_expr(self):
        speech = "call function quick sort parameter x with parameter j plus one parameter last end function"
        struct = "#function quickSort(#parameter #variable x #parameter #variable j + #value 1 #parameter #variable last);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_func_with_params_arr(self):
        speech = "call function def with parameter x parameter x array index i end function"
        struct = "#function def(#parameter #variable x #parameter #array x #indexes #variable i #index_end);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_assign_call_func(self):
        speech = "max equal call function def with parameter two end function end equal"
        struct = "#assign #variable max #with #function def(#parameter #value 2);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_if_call_func(self):
        speech = "begin if max less than call function def with parameter two end function then end if"
        struct = "if #condition #variable max < #function def(#parameter #value 2) #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_call_func(self):
        speech = "while call function def with parameter two end function begin end while"
        struct = "while #condition #function def(#parameter #value 2) #while_start #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_func_empty(self):
        speech = "call function do something end function"
        struct = "#function doSomething();;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_body_call_func(self):
        speech = "while i less than j begin call function do something end function end while"
        struct = "while #condition #variable i < #variable j #while_start #function doSomething();; #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_func_string(self):
        speech = "call function print f parameter string hello end string end function"
        struct = "#function printF(#parameter #value \"hello\");;"
        self.wordparser_compare(speech, struct)

        speech = "call function test parameter string hello world man end string end function"
        struct = "#function test(#parameter #value \"hello world man\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_func_string_multiple(self):
        speech = "call function abc parameter string hello end string with parameter string world end string end function"
        struct = "#function abc(#parameter #value \"hello\" #parameter #value \"world\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_declare_char_var(self):
        speech = "declare character c equal character c end declare"
        struct = "#create char #variable c #value 'c' #dec_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_switch_stmts(self):
        speech = "switch a case zero call function hello world end function break case one a equal two end equal break " + \
                    " default a equal three end equal end switch"
        struct = "switch #condition #variable a case #value 0 #case_start #function helloWorld();; break;; #case_end " + \
                    " case #value 1 #case_start #assign #variable a #with #value 2;; break;; #case_end " + \
                    " default #case_start #assign #variable a #with #value 3;; #case_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_switch_wo_default(self):
        speech = "switch a case zero call function hello world end function break case one a equal two end equal break " + \
                    " end switch"
        struct = "switch #condition #variable a case #value 0 #case_start #function helloWorld();; break;; #case_end " + \
                    " case #value 1 #case_start #assign #variable a #with #value 2;; break;; #case_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_switch_character(self):
        speech = "switch alphabet case character a call function x end function case character b x equal one end equal end switch "
        struct = "switch #condition #variable alphabet case #value 'a' #case_start #function x();; #case_end " + \
                    " case #value 'b' #case_start #assign #variable x #with #value 1;; #case_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_switch_condition_expr(self):
        speech = "switch a minus two case zero call function hello world end function break case one a equal two end equal break " + \
                    " default a equal three end equal end switch"
        struct = "switch #condition #variable a - #value 2 case #value 0 #case_start #function helloWorld();; break;; #case_end " + \
                    " case #value 1 #case_start #assign #variable a #with #value 2;; break;; #case_end " + \
                    " default #case_start #assign #variable a #with #value 3;; #case_end;; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_logical_and(self):
        speech = "begin if i less than two and j less than three then end if"
        struct = "if #condition #variable i < #value 2 && #variable j < #value 3 #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_logical_or(self):
        speech = "begin if i less than two or j less than three then end if"
        struct = "if #condition #variable i < #value 2 || #variable j < #value 3 #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_logical_and_or_multiple(self):
        speech = "begin if i less than two or j less than three and k greater than l and h less than o or l equal b then end if"
        struct = "if #condition #variable i < #value 2 || #variable j < #value 3 && #variable k > #variable l " + \
                 " && #variable h < #variable o || #variable l == #variable b #if_branch_start #if_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_logical_single_conditionals_multiple(self):
        speech = "begin if hello world and bye world or why world then a equal b end equal c equal d end equal " + \
                 "else e equal f end equal end if"
        struct = "if #condition #variable helloWorld && #variable byeWorld || #variable whyWorld #if_branch_start " + \
                 "#assign #variable a #with #variable b;; #assign #variable c #with #variable d;; #if_branch_end " + \
                 "#else_branch_start #assign #variable e #with #variable f;; #else_branch_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_logical_multiple_etc(self):
        speech = "while red tomato not equal five hundred and blue sofa less than twenty one begin end while"
        struct = "while #condition #variable redTomato != #value 500 && #variable blueSofa < #value 21 #while_start #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_complex_expressions(self):
        speech = "a equal b plus c minus two plus call function hello world end function end equal"
        struct = "#assign #variable a #with #variable b + #variable c - #value 2 + #function helloWorld();;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_complex_expressions_2(self):
        speech = "a equal call function hey end function plus two minus call function hello world end function end equal"
        struct = "#assign #variable a #with #function hey() + #value 2 - #function helloWorld();;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_conditional_logical_and(self):
        speech = "for loop condition i equal one condition i plus two less than length and j less than length minus alpha condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i + #value 2 < #variable length && #variable j < #variable length - #variable alpha #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_conditional_logical_or(self):
        speech = "for loop condition i equal one condition i plus j greater than equal length plus two or j less than length condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i + #variable j >= #variable length + #value 2 || #variable j < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_conditional_complex_expr(self):
        speech = "for loop condition i equal one " + \
                 "condition trigger value less than equal length plus two " + \
                 "or j less than length and k greater than control value " + \
                 "condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 " + \
                 "#condition #variable triggerValue <= #variable length + #value 2 " + \
                 "|| #variable j < #variable length && #variable k > #variable controlValue " + \
                 "#condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_conditional_lone_variables(self):
        speech = "for loop condition i equal one condition is done and is complete or has no wrong condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable isDone && #variable isComplete || #variable hasNoWrong #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_plus_equal_expr(self):
        speech = "max plus equal max plus one end equal"
        struct = "#assign #variable max += #variable max + #value 1;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_minus_equal_expr(self):
        speech = "max minus equal max plus one end equal"
        struct = "#assign #variable max -= #variable max + #value 1;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_times_equal_expr(self):
        speech = "max times equal max plus one end equal"
        struct = "#assign #variable max *= #variable max + #value 1;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_divide_equal_expr(self):
        speech = "max divide equal max plus one end equal"
        struct = "#assign #variable max /= #variable max + #value 1;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_var_modulo_equal_expr(self):
        speech = "max modulo equal max plus one end equal"
        struct = "#assign #variable max %= #variable max + #value 1;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_initial_plus_eq(self):
        speech = "for loop condition i plus equal max minus one condition i less than length condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i += #variable max - #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)
        

    # Word Parser - Test partial code
    def test_word_parser_partial_declare_var(self):
        speech = "declare integer abc "
        struct = "#create int #variable abc #dec_end;; "
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_partial_var_assign(self):
        speech = "max equal two"
        struct = "#assign #variable max #with #value 2;;"
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_partial_if(self):
        speech = "begin if x less than y then"
        struct = "if #condition #variable x < #variable y #if_branch_start #if_branch_end;;"
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_partial_for(self):
        speech = "for loop condition i equal one condition i less than two condition i plus plus begin"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #value 2 #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_multiple_stmts(self):
        speech = "begin if x less than y then max equal two"
        struct = "if #condition #variable x < #variable y #if_branch_start #assign #variable max #with #value 2;; #if_branch_end;;"
        self.wordparser_compare_correction(speech, struct)

    # Test Word Parser added variables
    def test_word_parser_added_variables_func_declare(self):
        speech = "create function find the tree with return type void with parameter integer wei he with parameter integer because begin end function"
        expected = ["find", "the", "tree", "wei", "he", "because"]

        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_func_declare_param_arr(self):
        speech = "create function find maximum return type void with parameter integer array wei he with parameter integer because " + \
                 " with parameter integer array hello begin end function"  
        expected = ["find", "maximum", "hello", "wei", "he", "because"]
        
        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_declare_variable_two_word(self):
        speech = "declare integer water bottle end declare"        
        expected = ["water", "bottle"]
        
        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_declare_variable_one_word(self):
        speech = "declare integer water end declare"        
        expected = ["water"]
        
        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_declare_array_one_word(self):
        speech = "declare integer array fire with size one end declare"        
        expected = ["fire"]
        
        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_declare_array_two_word(self):
        speech = "declare integer array fire alarm with size twenty two end declare"     
        expected = ["fire", "alarm"]
        
        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_declare_array_size_var_one_word(self):
        speech = "declare integer array fire alarm with size length end declare"     
        expected = ["fire", "alarm", "length"]
        
        self.wordparser_compare_added_variables(speech, expected)

    def test_word_parser_added_variables_declare_array_size_var_two_word(self):
        speech = "declare integer array fire alarm with size wei he end declare"     
        expected = ["fire", "alarm", "wei", "he"]
        
        self.wordparser_compare_added_variables(speech, expected)

    # Utility functions below.

    def wordparser_compare_added_variables(self, raw_text, expected):
        wordParser = WordParser()
        wordParser.parse(raw_text)
        
        expected.sort()

        variables = wordParser.get_variables()
        variables.sort()

        self.assertTrue(expected is not None)
        self.assertTrue(variables is not None)
        self.assertEqual(expected, variables)

    def wordparser_compare(self, raw_text, expected):
        wordParser = WordParser()
        parsed = self.trim_all_spaces(wordParser.parse(raw_text))
        expected = self.trim_all_spaces(expected)        
        self.assertEqual(parsed, expected)


    def wordparser_compare_correction(self, raw_text, expected):
        wordParser = WordParser()
        parsed = self.trim_all_spaces(wordParser.parse_with_correction(raw_text)["parsed"])
        expected = self.trim_all_spaces(expected)        
        self.assertEqual(parsed, expected)

    def trim_all_spaces(self, words):
        word = ' '.join(str(words).split())
        word = word.strip()

        return word
        

    def format_spaces(self, sentence):
        return ' '.join(sentence.split())
        

if __name__ == '__main__':
    unittest.main()
