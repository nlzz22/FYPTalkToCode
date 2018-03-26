#!/usr/bin/env python2

import unittest
from NewWordParser import WordParser
from WordCorrector import WordCorrector
import WordSimilarity
import StructuralCommandParser

class TestWordParserMethods(unittest.TestCase):
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

    def test_word_parser_for_loop_initial_plus_eq_with_arr(self):
        speech = "for loop condition numbers tree array index i plus equal max condition i less than length condition i plus plus begin end for loop"
        struct = "for #condition #assign #array numbersTree #indexes #variable i #index_end += #variable max #condition #variable i < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_with_end_equal(self):
        speech = "for loop condition i equal one end equal condition i less than length condition i plus plus end equal begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_postfix_assignment(self):
        speech = "max plus plus end equal"
        struct = "#post #variable max ++;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_postfix_assignment_2(self):
        speech = "time counter plus plus end equal"
        struct = "#post #variable timeCounter ++;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_prefix_assignment(self):
        speech = "plus plus max end equal"
        struct = "++ #variable max;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_prefix_assignment_2(self):
        speech = "plus plus splash counter end equal"
        struct = "++ #variable splashCounter;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_prefix_increment(self):
        speech = "for loop condition i equal one condition i less than length condition plus plus i begin end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition ++ #variable i #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_symbol(self):
        speech = "call function print that parameter string symbol dollar symbol percent symbol ampersand hello world symbol backslash n end string end function"
        struct = "#function printThat(#parameter #value \"$%&hello world \\n\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_scan_symbol(self):
        speech = "call function scan thing parameter string symbol percent c end string parameter symbol ampersand ch end function"
        struct = "#function scanThing(#parameter #value \"%c\" #parameter & #variable ch);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_print_symbol(self):
        speech = "call function print print parameter string entered character is symbol percent c symbol backslash n end string parameter ch end function"
        struct = "#function printPrint(#parameter #value \"entered character is %c \\n\" #parameter #variable ch);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_call_function_complex_string(self):
        speech = "call function a parameter string hello end string plus string world end string end function"
        struct = "#function a(#parameter #value \"hello\" + #value \"world\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_symbol_new(self):
        speech = "call function print with parameter string enter the value symbol colon symbol backslash n end string end function"
        struct = "#function print(#parameter #value \"enter the value :\\n\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_symbol_with_space(self):
        speech = "call function print with parameter string enter the value symbol colon space symbol dollar end string end function"
        struct = "#function print(#parameter #value \"enter the value : $\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_symbol_with_space_2(self):
        speech = "call function print with parameter string enter the value symbol colon space end string end function"
        struct = "#function print(#parameter #value \"enter the value : \");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_printf_percent_c_space(self):
        speech = "call function printf with parameter string symbol percent c space end string parameter character c end function"
        struct = "#function printf(#parameter #value \"%c \" #parameter #value 'c');;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_printf(self):
        speech = "call function printf parameter string symbol percent d end string parameter print end function"
        struct = "#function printf(#parameter #value \"%d\" #parameter #variable print);; "
        self.wordparser_compare(speech, struct)

    def test_word_parser_scanf(self):
        speech = "call function scanf parameter string symbol percent d end string parameter symbol ampersand print end function"
        struct = "#function scanf(#parameter #value \"%d\" #parameter & #variable print);;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_break(self):
        speech = "for loop condition i equal one condition i less than length condition i plus plus begin " + \
                 "begin if i equal ten then is done equal one end equal break end if end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length " + \
                 "#condition #post #variable i ++ #for_start " + \
                 "if #condition #variable i == #value 10 #if_branch_start #assign #variable isDone #with #value 1;; " + \
                 "break;; #if_branch_end;; #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_break(self):
        speech = "while i less than length begin " + \
                 "begin if i equal ten then is done equal one end equal break end if end while"
        struct = "while #condition #variable i < #variable length #while_start " + \
                 "if #condition #variable i == #value 10 #if_branch_start #assign #variable isDone #with #value 1;; " + \
                 "break;; #if_branch_end;; #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_continue(self):
        speech = "for loop condition i equal one condition i less than length condition i plus plus begin " + \
                 "begin if i equal ten then is done equal one end equal continue end if end for loop"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length " + \
                 "#condition #post #variable i ++ #for_start " + \
                 "if #condition #variable i == #value 10 #if_branch_start #assign #variable isDone #with #value 1;; " + \
                 "continue;; #if_branch_end;; #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_while_continue(self):
        speech = "while i less than length begin " + \
                 "begin if i equal ten then is done equal one end equal continue end if end while"
        struct = "while #condition #variable i < #variable length #while_start " + \
                 "if #condition #variable i == #value 10 #if_branch_start #assign #variable isDone #with #value 1;; " + \
                 "continue;; #if_branch_end;; #while_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_symbol_as_last_char(self):
        speech = "call function printf parameter string enter two numbers symbol colon end string end function"
        struct = "#function printf(#parameter #value \"enter two numbers :\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_symbol_equal_dot_with_alphanum_in_string(self):
        speech = "call function printf parameter string product symbol equal symbol percent symbol dot 2lf end string end function"
        struct = "#function printf(#parameter #value \"product =%.2lf\");;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_missing_first_cond(self):
        speech = "for loop condition condition i less than length condition i plus plus begin end for loop"
        struct = "for #condition #condition #variable i < #variable length #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_missing_second_cond(self):
        speech = "for loop condition i equal zero condition condition i plus plus begin end for loop"
        struct = "for #condition #assign #variable i #with #value 0 #condition #condition #post #variable i ++ #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_missing_third_cond(self):
        speech = "for loop condition i equal zero condition i less than length condition begin end for loop"
        struct = "for #condition #assign #variable i #with #value 0 #condition #variable i < #variable length #condition #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_missing_all_cond(self):
        speech = "for loop condition condition condition begin end for loop"
        struct = "for #condition #condition #condition #for_start #for_end;;"
        self.wordparser_compare(speech, struct)

    def test_word_parser_for_loop_missing_two_cond(self):
        speech = "for loop condition condition condition i plus plus begin end for loop"
        struct = "for #condition #condition #condition #post #variable i ++ #for_start #for_end;;"
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

    def test_word_parser_multiple_ifs(self):
        speech = "begin if i less than one then begin if i less than two then"
        struct = "if #condition #variable i < #value 1 #if_branch_start if #condition #variable i < #value 2 #if_branch_start #if_branch_end;; #if_branch_end;;"
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_fail_parse_end_function_end_string_end_function(self):
        speech = "call function scanf parameter string"
        struct = ""
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_partial_string(self):
        speech = "call function scanf parameter string hello world"
        struct = "#function scanf(#parameter #value \"hello world\");;"
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_partial_multiple_constructs(self):
        speech = "for loop condition i equal one condition i less than length condition i plus plus begin " + \
                 "begin if i less than max then " + \
                 "call function a parameter string hello end string parameter string why is this"
        struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start " + \
                 "if #condition #variable i < #variable max #if_branch_start " + \
                 "#function a(#parameter #value \"hello\" #parameter #value \"why is this\");; #if_branch_end;; #for_end;;"
        self.wordparser_compare_correction(speech, struct)

    def test_word_parser_partial_find_max(self):
        speech = "create function find maximum with return type integer with parameter integer array numbers " + \
                 "with parameter integer length begin declare integer max equal numbers array index zero end declare " + \
                 "declare integer i end declare " + \
                 "for loop condition i equal one condition i less than length condition i plus plus begin"
        struct = "#function_declare findMaximum int #parameter_a #dimension 1 int #array numbers " + \
                 "#parameter int length #function_start " + \
                "#create int #variable max #array numbers #indexes  #value 0 #index_end #dec_end;; " + \
                "#create int #variable i #dec_end;; " + \
                "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start " + \
                "#for_end;; #function_end;;"
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

    # Test Word Parser - multiple parts

    def test_word_parser_partial(self):
        speech = "max equal"
        expected_parsed = [""]
        expected_text = ["max equal"]
        expected_sent_status = [False]
        self.wordparser_compare_parts(speech, expected_parsed, expected_text, expected_sent_status)

    def test_word_parser_full(self):
        speech = "counter plus plus end equal"
        expected_parsed = ["#post #variable counter ++;;"]
        expected_text = ["counter plus plus end equal"]
        expected_sent_status = [True]
        self.wordparser_compare_parts(speech, expected_parsed, expected_text, expected_sent_status) 

    def test_word_parser_full_then_partial(self):
        speech = "declare integer max end declare declare integer"
        expected_parsed = ["#create int #variable max #dec_end;;", ""]
        expected_text = ["declare integer max end declare", "declare integer"]
        expected_sent_status = [True, False]
        self.wordparser_compare_parts(speech, expected_parsed, expected_text, expected_sent_status)

    def test_word_parser_full_then_full(self):
        speech = "declare integer max end declare declare integer min"
        expected_parsed = ["#create int #variable max #dec_end;;", "#create int #variable min #dec_end;;"]
        expected_text = ["declare integer max end declare", "declare integer min"]
        expected_sent_status = [True, True]
        self.wordparser_compare_parts(speech, expected_parsed, expected_text, expected_sent_status)

    def test_word_parser_full_twice_partial(self):
        speech = "declare integer max end declare declare integer min end declare declare integer"
        expected_parsed = ["#create int #variable max #dec_end;;", "#create int #variable min #dec_end;;", ""]
        expected_text = ["declare integer max end declare", "declare integer min end declare", "declare integer"]
        expected_sent_status = [True, True, False]
        self.wordparser_compare_parts(speech, expected_parsed, expected_text, expected_sent_status)

    def test_word_parser_full_thrice(self):
        speech = "declare integer max end declare declare integer min end declare declare integer first end declare"
        expected_parsed = ["#create int #variable max #dec_end;;", "#create int #variable min #dec_end;;", \
                           "#create int #variable first #dec_end;;"]
        expected_text = ["declare integer max end declare", "declare integer min end declare", \
                         "declare integer first end declare"]
        expected_sent_status = [True, True, True]
        self.wordparser_compare_parts(speech, expected_parsed, expected_text, expected_sent_status)

    # Test individual methods in word parser.

    def test_word_parser_need_to_append_end_equal(self):
        speech = "first equal one"
        
        wp = WordParser()
        self.assertTrue(wp.need_to_append_end_equal(speech))

    def test_word_parser_dont_append_end_equal_because_already_exists(self):
        speech = "first equal one end equal"
        
        wp = WordParser()
        self.assertFalse(wp.need_to_append_end_equal(speech))

    def test_word_parser_need_to_append_end_equal_plus_plus(self):
        speech = "first plus plus"
        
        wp = WordParser()
        self.assertTrue(wp.need_to_append_end_equal(speech))

    def test_word_parser_need_to_append_end_equal_minus_equal(self):
        speech = "first minus equal one"
        
        wp = WordParser()
        self.assertTrue(wp.need_to_append_end_equal(speech))

    def test_word_parser_dont_append_end_equal_because_conditional_if(self):
        speech = "begin if i equal two"
        
        wp = WordParser()
        self.assertFalse(wp.need_to_append_end_equal(speech))

    def test_word_parser_dont_append_end_equal_because_conditional_if2(self):
        speech = "begin if i equal two then"
        
        wp = WordParser()
        self.assertFalse(wp.need_to_append_end_equal(speech))

    def test_word_parser_dont_append_end_equal_because_conditional_while(self):
        speech = "while i equal two"
        
        wp = WordParser()
        self.assertFalse(wp.need_to_append_end_equal(speech))

    def test_word_parser_dont_append_end_equal_because_conditional_for(self):
        speech = "for loop condition i equal two"
        
        wp = WordParser()
        self.assertFalse(wp.need_to_append_end_equal(speech))

    def test_word_parser_dont_append_end_declare_because_already_exists(self):
        speech = "declare integer flying equal two end declare"
        
        wp = WordParser()
        self.assertFalse(wp.need_to_append_end_declare(speech))

    def test_word_parser_need_to_append_end_declare(self):
        speech = "declare integer flying equal two"
        
        wp = WordParser()
        self.assertTrue(wp.need_to_append_end_declare(speech))

    # Utility functions below.

    def wordparser_compare_parts(self, raw_text, expected_parsed, expected_text, expected_sent_status):
        wordParser = WordParser()
        struct = wordParser.parse(raw_text)
        actual_parsed = struct["parsed"]
        actual_text = struct["text"]
        actual_status = struct["sentence_status"]
        self.assertEqual(expected_parsed, actual_parsed)
        self.assertEqual(expected_text, actual_text)
        self.assertEqual(expected_sent_status, actual_status)
        

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
        parsed = self.trim_all_spaces(wordParser.parse(raw_text)["parsed"][0])
        expected = self.trim_all_spaces(expected)        
        self.assertEqual(parsed, expected)


    def wordparser_compare_correction(self, raw_text, expected):
        wordParser = WordParser()
        parsed = self.trim_all_spaces(wordParser.parse(raw_text)["parsed"][0])
        expected = self.trim_all_spaces(expected)        
        self.assertEqual(parsed, expected)

    def trim_all_spaces(self, words):
        word = ' '.join(str(words).split())
        word = word.strip()

        return word
        
    def format_spaces(self, sentence):
        return UtilityClass().format_spaces(sentence)


class TestWordCorrectorMethods(unittest.TestCase):
    def test_word_corrector_variables(self):
        word = "eye equal one end equal "
        word += "next equal two end equal"
        wc = WordCorrector(word, ["max", "i"])
        corrected = wc.run_correction()
        expected = "i equal one end equal max equal two end equal"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))


    def test_word_corrector_variables_escape_words_declare(self):
        word = "declare integer eye end declare"
        wc = WordCorrector(word, ["max", "i"])
        corrected = wc.run_correction()
        expected = word # no correction as word starts with escape word "declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_variables_escape_words_create_func(self):
        word = "create function find maximum with return type integer begin end function"
        wc = WordCorrector(word, ["max", "bind", "mind"])
        corrected = wc.run_correction()
        expected = word # no correction as word starts with escape word "create function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_variables_string_literal(self):
        word = "call function find parameter string next end string end function"
        wc = WordCorrector(word, ["max", "mind"])
        corrected = wc.run_correction()
        expected = "call function mind parameter string next end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_variables_character_literal(self):
        word = "max equal character a end declare"
        wc = WordCorrector(word, ["max", "eh", "aa"])
        corrected = wc.run_correction()
        expected = word
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_normal(self):
        word = "for Loop condition is equal one condition I less than length condition I plus plus begin \
         if numbers array index I greater than Max Den Max equal numbers array index I and equal and if and for Loop return Max \
         and function"
        wc = WordCorrector(word, ["max", "length", "i", "numbers"])
        corrected = wc.run_correction()
        expected = "for loop condition i equal one condition i less than length condition i plus plus begin \
            if numbers array index i greater than max then max equal numbers array index i end equal \
            end if end for loop return max end function"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_condition_is(self):
        word = "for Loop condition is equal two condition is less than equal number divided 2 condition I plus plus begin "
        wc = WordCorrector(word, ["i", "number"])
        corrected = wc.run_correction()
        expected = "for loop condition i equal two condition i less than equal number divide two condition i plus plus begin"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_condition_miss_iterator(self):
        word = "for loop condition equal two condition less than equal number condition i plus plus begin "
        wc = WordCorrector(word, ["i", "number"])
        corrected = wc.run_correction()
        expected = "for loop condition i equal two condition i less than equal number condition i plus plus begin "
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_condition_miss_iterator_2(self):
        word = "for loop condition equal two condition less than equal number condition j plus plus begin "
        wc = WordCorrector(word, ["j", "number"])
        corrected = wc.run_correction()
        expected = "for loop condition j equal two condition j less than equal number condition j plus plus begin "
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_condition_divided_by_correction(self):
        word = "for loop condition i equal two condition less than equal number divided by 2 condition i plus plus begin "
        wc = WordCorrector(word, ["i", "number"])
        corrected = wc.run_correction()
        expected = "for loop condition i equal two condition i less than equal number divide two condition i plus plus begin "
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_num_to_alpha(self):
        word = "sequence array index 0 equal 1 end equal"
        wc = WordCorrector(word, ["sequence"])
        corrected = wc.run_correction()
        expected = "sequence array index zero equal one end equal"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))
        

    def test_word_corrector_call_func(self):
        word = "call function hello world width parameter string how are you end string end function"
        wc = WordCorrector(word, ["hello", "world"])
        corrected = wc.run_correction()
        expected = "call function hello world with parameter string how are you end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_bug_with_four(self):
        word = "sequence array index three equal four end equal"
        wc = WordCorrector(word, ["sequence"])
        corrected = wc.run_correction()
        expected = word
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))


    def test_word_corrector_bug_with_no_whole_word_replace(self):
        word = "for loop condition i equal one"
        wc = WordCorrector(word, ["eye"])
        corrected = wc.run_correction()
        expected = "for loop condition eye equal one"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_ii_to_i(self):
        word = "first equal II end equal"
        wc = WordCorrector(word, ["first", "i"])
        corrected = wc.run_correction()
        expected = "first equal i end equal"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_ii_to_second(self):
        word = "first equal II end equal"
        wc = WordCorrector(word, ["first", "second"])
        corrected = wc.run_correction()
        expected = "first equal second end equal"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_ii_to_none(self):
        word = "first equal II end equal"
        wc = WordCorrector(word, ["first"])
        corrected = wc.run_correction()
        expected = word.lower()
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_equal_to(self):
        word = "declare integer second equal to end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer second equal two end declare"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_do_not_correct_equal_to(self):
        word = "declare integer second equal to end declare"
        wc = WordCorrector(word, ["to"])
        corrected = wc.run_correction()
        expected = "declare integer second equal to end declare"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_bug_declare_var_to(self):
        word = "declare integer to end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = word
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_printf(self):
        word = "call function print f parameter string symbol percent d end string parameter print end function"
        wc = WordCorrector(word, ["print", "wink"])
        corrected = wc.run_correction()
        expected = "call function printf parameter string symbol percent d end string parameter print end function"
        
        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_printf_bug(self):
        word = "call function print F parameter string hello world end string and function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        
        expected = "call function printf parameter string hello world end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_scanf(self):
        word = "call function scan f parameter string symbol percent d end string parameter symbol ampersand print end function"
        wc = WordCorrector(word, ["print", "wink"])
        corrected = wc.run_correction()
        expected = "call function scanf parameter string symbol percent d end string parameter symbol ampersand print end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_integer(self):
        word = "declare in detail max equal one end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal one end declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_wrong_declare(self):
        word = "degree integer max equal one end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal one end declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_end_declare(self):
        word = "declare integer max equal one end degree"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal one end declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_declare_many_errors(self):
        word = "degree integer max equal one end degree"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal one end declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_wrong_create_func(self):
        word = "crate junction find maximum with return type integer with parameter float array numbers begin"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "create function find maximum with return type integer with parameter float array numbers begin"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_create_func_many_errors(self):
        word = "crate junction find maximum width written type in detail with perimeter float array numbers begin"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "create function find maximum with return type integer with parameter float array numbers begin"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_string_with_errors(self):
        word = "call junction maximum width perimeter string hello world end string perimeter length end junction "
        wc = WordCorrector(word, ["maximum", "length"])
        corrected = wc.run_correction()
        expected = "call function maximum with parameter string hello world end string parameter length end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_dont_correct_double_var_types(self):
        # integer length will be corrected to integer long , if we do not implement the blocking mechanism for
        # consecutive variable types.
        word = "create function find maximum with parameter integer length with parameter integer array numbers begin"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_dont_correct_create_func_var(self):
        # length will be corrected to long , if we do not implement the blocking mechanism for
        # create function.
        word = "create function length with parameter integer length with parameter integer array numbers begin"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_declare_index(self):
        word = "declare integer max equal numbers array index 0 end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal numbers array index zero end declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_begin_if(self):
        word = "begin is numbers array index i greater dan mex then"
        wc = WordCorrector(word, ["numbers", "max", "i"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index i greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_end_if(self):
        word = "end eve"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "end if"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_var_type_after_return_type(self):
        word = "create function main with return type voice begin end function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "create function main with return type void begin end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_var_type_after_declare(self):
        word = "declare coat max equal one end declare"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare float max equal one end declare"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_reef(self):
        word = "create function main reef return type void begin end function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "create function main with return type void begin end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_dont_correct_reef(self):
        word = "create function main reef return type void begin end function"
        wc = WordCorrector(word, ["reef"])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_infinite_loop_string(self):
        word = "string a b c d"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_character_nonetype_error(self):
        word = "character"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_multiple_sentences_same(self):
        word = "declare integer max equal one end declare declare in detail min"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal one end declare declare integer min"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_multiple_sentences_diff(self):
        word = "declare integer max equal one and declare declare in detail min and declare max equal one"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer max equal one end declare declare integer min end declare max equal one"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_mine_is_to_minus(self):
        word = "energy mine is mine is"
        wc = WordCorrector(word, ["energy"])
        corrected = wc.run_correction()
        expected = "energy minus minus"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_sequent_to_equal(self):
        word = "Max sequent Energy"
        wc = WordCorrector(word, ["energy", "max"])
        corrected = wc.run_correction()
        expected = "max equal energy"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_than_to_then(self):
        # special case, "than" is only correct if "greater" or "less" comes before it.
        word = "begin if numbers array index i greater than Max than"
        wc = WordCorrector(word, ["numbers", "i", "max"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index i greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_then_to_than(self):
        # corrects "greater then" to "greater than"
        word = "begin if numbers array index i greater then Max then"
        wc = WordCorrector(word, ["numbers", "i", "max"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index i greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_than_then_dilemma(self):
        # A combination of both test cases.
        word = "begin if numbers array index i greater then Max than"
        wc = WordCorrector(word, ["numbers", "i", "max"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index i greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_end_this_to_end_if(self):
        word = "end this"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "end if"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_begin_this_possible_east(self):
        word = "create function main with return type void begin east equal one end function"
        wc = WordCorrector(word, ["east"])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_add(self):
        word = "declare integer first equal 1 + 2"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer first equal one plus two"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_divide(self):
        word = "declare integer first equal 1/2"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer first equal one divide two"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_minus(self):
        word = "declare integer first equal 1 - 2"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer first equal one minus two"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_times(self):
        word = "declare integer first equal 1 x 2"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer first equal one times two"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_capital_x_as_times(self):
        word = "declare integer first equal 1 X 2"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer first equal one times two"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_star_as_times(self):
        word = "declare integer first equal 1 * 2"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer first equal one times two"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_symbol_dot(self):
        word = "call function printf parameter string symbol. end string end function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "call function printf parameter string symbol dot end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_end_string(self):
        word = "call function print f parameter string hello world and string end function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "call function printf parameter string hello world end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_do_not_correct_to_symbol_keyword(self):
        # symbol keyword ampersand is closest to thailand, but it is not correct as this is not a symbol.
        word = "thailand equal one end equal"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "ampersand equal one end equal"

        self.assertNotEqual(self.format_spaces(corrected), self.format_spaces(expected)) # assert !=

    def test_word_corrector_correct_symbol_keyword(self):
        word = "call function print f parameter string symbol thailand symbol ascent end string end function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "call function printf parameter string symbol ampersand symbol percent end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_symbol_without_keyword(self):
        word = "call function printf parameter string symbol"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = word

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_symbol_keyword_partial(self):
        word = "call function print f parameter string symbol thailand"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "call function printf parameter string symbol ampersand"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_and_percent_to_ampersand(self):
        word = "call function scan f parameter string symbol percent lf symbol percent lf end string " + \
               "parameter symbol and percent first number parameter symbol and percent second number end function"
        wc = WordCorrector(word, ["first", "second", "number"])
        corrected = wc.run_correction()
        expected = "call function scanf parameter string symbol percent lf symbol percent lf end string " + \
               "parameter symbol ampersand first number parameter symbol ampersand second number end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_and_person_to_ampersand(self):
        word = "call function scan f parameter string symbol percent lf symbol percent lf end string " + \
               "parameter symbol and person first number parameter symbol and person second number end function"
        wc = WordCorrector(word, ["first", "second", "number"])
        corrected = wc.run_correction()
        expected = "call function scanf parameter string symbol percent lf symbol percent lf end string " + \
               "parameter symbol ampersand first number parameter symbol ampersand second number end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_in_person_to_ampersand(self):
        word = "call function scan f parameter string symbol percent D end string " + \
               "parameter symbol in person number and function"
        wc = WordCorrector(word, ["number"])
        corrected = wc.run_correction()
        expected = "call function scanf parameter string symbol percent D end string " + \
               "parameter symbol ampersand number end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_do_not_correct_symbol_word_in_diff_case(self):
        word = "call function scan f parameter string symbol percent lf symbol percent lf end string " + \
               "parameter symbol Ampersand first number parameter symbol and percent second number and function"
        wc = WordCorrector(word, ["first", "second", "number"])
        corrected = wc.run_correction()
        expected = "call function scanf parameter string symbol percent lf symbol percent lf end string " + \
               "parameter symbol ampersand first number parameter symbol ampersand second number end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_do_not_correct_keyword_in_diff_case(self):
        word = "Call Function Print f parameter String a b c end string end function "
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "Call Function printf parameter String a b c end string end function ".lower()

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_character_corner_case(self):
        word = "for Loop condition c equal character a condition see less than equal corrector Z condition plus plus c begin  "
        wc = WordCorrector(word, ["c"])
        corrected = wc.run_correction()
        expected = "for loop condition c equal character a condition c less than equal character z condition plus plus c begin  "

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_post_declare_integer_wrong_correction(self):
        word = "declare integer count equals 0"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "declare integer count equal zero" # previously corrected to "declare integer equal zero"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_rhyme_1_correction(self):
        word = "begin if numbers array index high greater than max then"
        wc = WordCorrector(word, ["numbers", "i", "max"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index i greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_printf_sim_correction(self):
        word = "call function princess parameter stream hello world end string end function"
        wc = WordCorrector(word, [])
        corrected = wc.run_correction()
        expected = "call function printf parameter string hello world end string end function"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_index_i_correct(self):
        word = "begin if numbers array index is greater than max then"
        wc = WordCorrector(word, ["numbers", "i", "max"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index i greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_index_number_no_correct(self):
        word = "begin if numbers array index 0 greater than max then"
        wc = WordCorrector(word, ["numbers", "i", "max"])
        corrected = wc.run_correction()
        expected = "begin if numbers array index zero greater than max then"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))

    def test_word_corrector_correct_wrong_if(self):
        word = "if equal two end equal"
        wc = WordCorrector(word, ["leave"])
        corrected = wc.run_correction()
        expected = "leave equal two end equal"

        self.assertEqual(self.format_spaces(corrected), self.format_spaces(expected))
    


    def format_spaces(self, sentence):
        return UtilityClass().format_spaces(sentence)

class TestWordSimilarityMethods(unittest.TestCase):
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

    def test_word_similarity_printf(self):
        word = "printf"
        list_vars = ["print", "f"]
        expected = "printf"
        most_sim_word = WordSimilarity.get_most_similar_word(word, list_vars)

        self.assertEqual(self.format_spaces(most_sim_word), self.format_spaces(expected))

    def format_spaces(self, sentence):
        return UtilityClass().format_spaces(sentence)


class TestStructuredCommandParserMethods(unittest.TestCase):
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

    def format_spaces(self, sentence):
        return UtilityClass().format_spaces(sentence)

class UtilityClass:
    def format_spaces(self, sentence):
        return ' '.join(sentence.split())
        

if __name__ == '__main__':
    test_res = []
    
    ## Word Corrector ##
    word_corrector_suite = unittest.TestLoader().loadTestsFromTestCase(TestWordCorrectorMethods)
    test_res.append(unittest.TextTestRunner(verbosity=1).run(word_corrector_suite))

    ## Word Similarity ##
    word_similarity_suite = unittest.TestLoader().loadTestsFromTestCase(TestWordSimilarityMethods)
    test_res.append(unittest.TextTestRunner(verbosity=1).run(word_similarity_suite))

    ## Struct Cmd Parser ##
    struct_cmd_parser_suite = unittest.TestLoader().loadTestsFromTestCase(TestStructuredCommandParserMethods)
    test_res.append(unittest.TextTestRunner(verbosity=1).run(struct_cmd_parser_suite))

    ## Word Parser ##
    word_parser_suite = unittest.TestLoader().loadTestsFromTestCase(TestWordParserMethods)
    test_res.append(unittest.TextTestRunner(verbosity=1).run(word_parser_suite))

    print "============================================"
    for test_result in test_res:
        test_result.printErrors()
