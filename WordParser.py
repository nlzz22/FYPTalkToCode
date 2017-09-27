from word2number import w2n # External library to parse words to numbers
from WordCorrector import WordCorrector

class WordParser:
    def __init__(self, words):
        self.NUM_TIMES_TO_CORRECT = 5
        
        self.structured_command = ""
        self.words_to_parse = self.correct_words(words).split(" ")
        self.variable_name_builder = ""
        self.number_list = w2n.american_number_system
        self.begin_stack = Stack() # wait for begin keyword
        self.end_stack = Stack() # wait for end keyword
        self.operators = ["plus", "minus", "times", "divide", "modulo"]
        self.comparison_ops = ["less", "greater", "not"]

    def correct_words(self, words):
        wordCorrector = WordCorrector(words)
        corrected = wordCorrector.run_correct_words_multiple("")
        return corrected
        

    def map_word_to_structured_command(self):
        while (self.has_next_word()):
            self.process_mapping()

        self.add_variable_name()

        return self.structured_command

    def process_mapping(self):
        word = self.get_next_word()
        
        if (word == "create"):
            if (self.has_next_word()):
                second_word = self.query_next_word()
                if (second_word == "function"):
                    self.get_next_word()
                    self.add_variable_name()
                    self.structured_command += " #function_declare"
                    self.begin_stack.push(Stack.FUNCTION_STACK)
                    self.end_stack.push(Stack.FUNCTION_STACK)
                else:
                    pass # unknown word to parse
            else:
                pass # unknown word to parse
        elif (word == "with"):
            pass # with is an optional word.
        elif (word == "return"):
            if (self.has_next_word()):
                second_word = self.query_next_word()
                if (second_word == "type"):
                    self.get_next_word()
                    self.add_variable_name()
                    var_type = self.process_variable_type()
                    if (var_type is not None):
                        self.structured_command += var_type
                else:
                    # return variable / number
                    self.structured_command += " return"
                    self.process_right_hand_side_of_operator()
                    self.structured_command += ";;"
            else:
                self.add_variable_name()
                self.structured_command += " return ;;"
        elif (word == "parameter"):
            self.add_variable_name()
            self.process_parameter()
        elif (word == "begin"):
            self.add_variable_name()
            self.process_begin()
        elif (word == "then"):
            if (self.begin_stack.peek() == Stack.IF_STACK):
                self.begin_stack.pop()
                self.structured_command += " #if_branch_start"
            elif (self.begin_stack.peek() == Stack.ELSE_STACK):
                self.begin_stack.pop()
                self.structured_command += " #else_branch_start" 
            else:
                pass # unknown
        elif (word == "else"):
            self.begin_stack.push(Stack.ELSE_STACK)
            
            if (self.end_stack.peek() == Stack.IF_STACK):
                self.end_stack.pop()
                self.end_stack.push(Stack.ELSE_STACK)
                self.structured_command += " #if_branch_end #else_branch_start"
            else:
                pass # unknown
        elif (word == "declare"):
            self.add_variable_name()
            self.process_var_declaration()
        elif (word == "end"):
            self.add_variable_name()
            self.process_end_construct()
        elif (word == "for" or word == "fall"):
            self.add_variable_name()
            if (self.has_next_word()):
                loop_word = self.query_next_word()
                if (loop_word == "loop"):
                    self.get_next_word()

                self.structured_command += " for"
                self.begin_stack.push(Stack.FOR_STACK)
                self.end_stack.push(Stack.FOR_STACK)
            else:
                pass # unknown word to parse
        elif (word == "if"):
            self.add_variable_name()
            self.structured_command += " if #condition"
            self.begin_stack.push(Stack.IF_STACK)
            self.end_stack.push(Stack.IF_STACK)
            
        elif (word == "condition"):
            self.add_variable_name()
            self.structured_command += " #condition"
        elif (word == "equal"):
            if (self.begin_stack.peek() == Stack.IF_STACK or self.begin_stack.peek() == Stack.ELSE_STACK):
                # equality
                self.process_comparison_ops(word)
            else:
                # assume variable beforehand
                self.structured_command += " #assign #variable"
                self.add_variable_name()
                self.structured_command += " #with"

                self.process_right_hand_side_of_operator()
        elif (word in self.operators):
            self.process_operators(word)
        elif (word in self.comparison_ops):
            self.process_comparison_ops(word)
        elif (word in self.number_list):
            self.reinsert_word(word)
            self.process_read_number_with_value_prefix()
        elif (word == "array"):
            self.process_array()
        else: # variable name
            self.append_part_build_var_name(word)



    def process_array(self):
        if (self.has_next_word()):
            next_word = self.get_next_word()
            if (next_word == "index"):
                self.handle_array_index("")
            else:
                pass # unknown error
        else:
            pass # unknown error
        pass # numbers array index i

    def process_comparison_ops(self, word):
        # assume condition before: less , greater, not
        if self.query_latest_added_word() != "#index_end": # if array, means already declared
            self.structured_command += " #variable"
            self.add_variable_name()        

        if (word == "less"):
            self.structured_command += " <"
            self.process_comparison_ops_query_equal()
        elif (word == "greater"):
            self.structured_command += " >"
            self.process_comparison_ops_query_equal()
        elif (word == "not"):
            self.structured_command += " !"
            self.process_comparison_ops_query_equal()
        elif (word == "equal"):
            self.structured_command += " =="

        self.process_right_hand_side_of_operator()

    def process_comparison_ops_query_equal(self):
        if (self.has_next_word()):
            next_word = self.get_next_word()
            if (next_word == "than"):
                if (self.has_next_word()):
                    next_word = self.query_next_word()
                    if (next_word == "equal"):
                        self.structured_command += "="
                    else:
                        pass # pure comparison without equal sign needed.
                else:
                    pass # error
                
            elif (next_word == "equal"):
                self.structured_command += "="
            else:
                # Error
                pass
                
        else:
            # Error
            pass
        

    def process_operators(self, word):
        has_right_side = True
            
        if (word == "times"):
            self.structured_command += " * "
        elif (word == "divide"):
            self.structured_command += " / "
        elif (word == "modulo"):
            self.structured_command += " % "
        elif (word == "plus"):
            if (self.has_next_word()):
                next_word = self.query_next_word()
                if (next_word == "plus"):
                    # plus plus
                    self.get_next_word()
                    self.structured_command += " #post #variable"
                    self.add_variable_name()
                    self.structured_command += " ++"
                    has_right_side = False
                else:
                    # plus only
                    self.structured_command += " + "
            else:
                pass # error
        elif (word == "minus"):
            if (self.has_next_word()):
                next_word = self.query_next_word()
                if (next_word == "minus"):
                    # minus minus
                    self.get_next_word()
                    self.structured_command += " #post #variable"
                    self.add_variable_name()
                    self.structured_command += " --"
                    has_right_side = False
                else:
                    # minus only
                    self.structured_command += " - "
            else:
                pass # error
        else:
            pass # error

        if (has_right_side):
            self.process_right_hand_side_of_operator()

    def process_right_hand_side_of_operator(self):
        if (self.has_next_word()):
            next_word = self.query_next_word()
            if (next_word in self.number_list):
                # numbers
                self.process_read_number_with_value_prefix()
            else:
                # variable
                self.read_variable_name_until_stop_words(["condition", "end", "array", "plus", "minus", "times", "divide", "modulo", "then", "begin"])

                if (self.has_next_word()):
                    next_word = self.query_next_word()
                    if (next_word == "array"):
                        self.get_next_word()
                        if (self.has_next_word()):
                            next_word = self.get_next_word()
                            if next_word == "index":
                                self.handle_array_index(";;")
                            else:
                                # Error
                                self.structured_command += ";;"
                        else:
                            self.structured_command += ";;"
                    else:
                        self.structured_command += " #variable"
                        self.add_variable_name()
                else:
                    self.structured_command += " #variable"
                    self.add_variable_name()
                    self.structured_command += ";;"
                
        else:
            pass # unknown word to parse

    def process_var_declaration(self):
        var_type = self.process_variable_type()
        if (var_type is None):
            pass # unknown word to parse
        else:
            if (self.has_next_word()):
                next_word = self.query_next_word()
                if (next_word == "array"):
                    self.read_variable_name_until_stop_words(["end", "size"])
                    if (self.has_next_word()):
                        next_word = self.get_next_word()
                        if (next_word == "size"):
                            # check number or variable
                            if (self.has_next_word()):
                                next_word = self.query_next_word()
                                if (next_word in self.number_list):
                                    # number
                                    number_read = self.read_numbers_until_no_more_numbers()
                                    number_parsed = w2n.word_to_num(number_read) # convert word to number
                                    self.structured_command += " #create" + var_type + " #array #variable"
                                    self.add_variable_name()
                                    self.structured_command += " #indexes #value " + str(number_parsed) + " #index_end"
                                else:
                                    # variable
                                    self.structured_command += " #create" + var_type + " #array #variable"
                                    self.add_variable_name()
                                    self.read_variable_name_until_stop_words(["end"])
                                    
                                    self.structured_command += " #indexes #variable "
                                    self.add_variable_name()
                                    self.structured_command += " #index_end"
                                    
                            else:
                                # error
                                self.structured_command += " #create" + var_type + " #variable"
                                self.add_variable_name()
                                self.structured_command += " #dec_end;;"                            
                        elif (next_word == "end"):
                            # error
                            self.structured_command += " #create" + var_type + " #variable"
                            self.add_variable_name()
                            self.structured_command += " #dec_end;;"
                        else:
                            pass # code should not reach here.
                    else:
                        # error
                        self.structured_command += " #create" + var_type + " #variable"
                        self.add_variable_name()
                        self.structured_command += " #dec_end;;"
                else:
                    # not an array
                    self.read_variable_name_until_stop_words(["end", "equal", "size"])
                    self.structured_command += " #create" + var_type + " #variable"
                    self.add_variable_name()

                    # Right hand side assignment if any
                    if (self.has_next_word()):
                        next_word = self.get_next_word()
                        if (next_word == "end"):
                            self.process_end_declare()
                        elif (next_word == "equal"): # right hand side assignment (equal to ?)
                            if (self.has_next_word()):
                                next_word = self.query_next_word()
                                if (next_word in self.number_list):
                                    # equal to a number
                                    self.process_read_number_with_value_prefix()
                                else:
                                    # variable / array
                                    self.read_variable_name_until_stop_words(["array", "end"])

                                    if (self.has_next_word()):
                                        next_word = self.get_next_word()
                                        if (next_word == "array"):
                                            if (self.has_next_word()):
                                                next_word = self.get_next_word()
                                                if (next_word == "index"):
                                                    self.handle_array_index(" #dec_end;;")
                                                else:
                                                    # error input
                                                    self.handle_error_assign_variable_when_declaring()
                                            else:
                                                self.handle_error_assign_variable_when_declaring() 
                                        elif (next_word == "end"):
                                            self.structured_command += " #variable"
                                            self.add_variable_name()
                                            self.process_end_declare()
                                        else:
                                            pass # code will not reach here
                                    else:
                                        self.handle_error_assign_variable_when_declaring()                                   
                                    
                            else:
                                self.structured_command += " #dec_end;;" # error input, terminate declaration
                        else:
                            self.structured_command += " #dec_end;;" # error input, terminate declaration
                    else:
                        self.structured_command += " #dec_end;;"
            else:
                pass # unknown word to parse

    def handle_array_index(self, custom_error):
        if (self.has_next_word()):
            self.structured_command += " #array "
            self.add_variable_name()
            self.structured_command += " #indexes "
            
            next_word = self.query_next_word()
            if (next_word in self.number_list):
                # number
                self.process_read_number_with_value_prefix()
                self.structured_command += " #index_end"
            else:
                # variable
                stop_words = ["end", "equal"] + self.operators + self.comparison_ops
                self.read_variable_name_until_stop_words(stop_words) 
                
                self.structured_command += " #variable "
                self.add_variable_name()
                self.structured_command += " #index_end"
        else:
            # Error
            self.structured_command += custom_error


    def process_end_declare(self):
        if (self.has_next_word()):
            next_word = self.get_next_word()
            if (next_word == "declare"):
                self.structured_command += " #dec_end;;"
            else:
                self.reinsert_word(next_word)
                self.structured_command += " #dec_end;;" # error input
        else:
            self.structured_command += " #dec_end;;"


    def process_end_construct(self):
        if (self.has_next_word()):
            construct = self.get_next_word()
            if (construct == "function"):
                self.structured_command += " #function_end;;"
                if (self.end_stack.peek() == Stack.FUNCTION_STACK):
                    self.end_stack.pop()
            elif (construct == "equal"):
                self.structured_command += ";;"
            elif (construct == "declare"):
                self.structured_command += " #dec_end;;"
            elif (construct == "for"):
                self.structured_command += " #for_end;;"
                if (self.end_stack.peek() == Stack.FOR_STACK):
                    self.end_stack.pop()

                # Remove additional "loop" word if any
                if (self.has_next_word()):
                    loop_word = self.query_next_word()
                    if (loop_word == "loop"):
                        self.get_next_word()
                    else:
                        pass # word is not loop, ignore
                else:
                    pass
            elif (construct == "if"):
                if (self.end_stack.peek() == Stack.IF_STACK):
                    self.end_stack.pop()
                    self.structured_command += " #if_branch_end;;"
                elif (self.end_stack.peek() == Stack.ELSE_STACK):
                    self.end_stack.pop()
                    self.structured_command += " #else_branch_end;;"
                else:
                    # unknown, just terminate.
                    pass                 
            else:
                # unknown, get from stack instead.
                self.process_end_construct_from_stack()
        else:
            self.process_end_construct_from_stack()


    def process_end_construct_from_stack(self):
        construct_to_end = self.end_stack.pop()
        if (construct_to_end is None):
            # error, ignore
            pass
        elif (construct_to_end == Stack.FUNCTION_STACK):
            self.structured_command += " #function_end;;"
        elif (construct_to_end == Stack.FOR_STACK):
            self.structured_command += " #for_end;;"
        elif (construct_to_end == Stack.IF_STACK):
            self.structured_command += " #if_branch_end;;"
        elif (construct_to_end == Stack.ELSE_STACK):
            self.structured_command += " #else_branch_end;;"
        else:
            # unknown, end
            pass

    def handle_error_assign_variable_when_declaring(self):
        self.structured_command += " #variable"
        self.add_variable_name()
        self.structured_command += " #dec_end;;"

    def process_parameter(self):
        var_type = self.process_variable_type()
        if (var_type is None):
            pass # unknown word to parse
        else:
            if (self.has_next_word()):
                next_word = self.query_next_word()
                if (next_word == "array"):
                    self.get_next_word()
                    self.structured_command += " #parameter_a #dimension 1" + var_type + " #array"
                    # #parameter_a #dimension 1 int #array X 
                else:
                    # not an array
                    self.structured_command += " #parameter " + var_type
            else:
                pass # unknown word to parse

           
    def process_begin(self):
        start_construct = self.begin_stack.pop()
        if (start_construct == None):
            pass # unknown begin word found
        elif (start_construct == Stack.FUNCTION_STACK):
            self.structured_command += " #function_start"
        elif (start_construct == Stack.FOR_STACK):
            self.structured_command += " #for_start"
        else:
            pass # unknown begin word found
            

    def process_variable_type(self):
        if (self.has_next_word()):
            word = self.get_next_word()
            if (word == "integer"):
                return " int" 
            elif (word == "boolean"):
                # Note: C program should not have boolean
                return " boolean"
            elif (word == "character"):
                return " char"
            elif (word == "double"):
                return " double"
            elif (word == "float"):
                return " float"
            elif (word == "long"):
                return " long"
            elif (word == "void"):
                return " void"
            elif (word == "in"):
                # Handles misread integer words: in the jar, in detail, in the jail, in to jail, in the job
                if (self.has_next_word()):
                    second_word = self.get_next_word()
                    if (second_word == "detail"):
                        return " int"
                    elif (second_word == "the" or second_word == "to"):
                        if (self.has_next_word()):
                            third_word = self.get_next_word()
                            if (third_word == "jar" or third_word == "jail" or third_word == "job"):
                                return " int"
                            else:
                                self.reinsert_word(third_word)
                                return " int"
                        else:
                            return " int"
                    else:
                        self.reinsert_word(second_word)
                        return " int"
                else:
                    return " int"
            else:
                return None # unknown variable type
        else:
            return None # unknown word to parse

    def process_read_number_with_value_prefix(self):
        number_read = self.read_numbers_until_no_more_numbers()
        number_parsed = w2n.word_to_num(number_read) # convert word to number
        self.structured_command += " #value " + str(number_parsed)

    def has_next_word(self):
        return len(self.words_to_parse) > 0

    def get_next_word(self):
        return self.words_to_parse.pop(0).lower()

    def reinsert_word(self, word):
        self.words_to_parse.insert(0, word)

    def query_next_word(self):
        return self.words_to_parse[0].lower()

    def add_variable_name(self):
        if (self.variable_name_builder is not None and self.variable_name_builder != ""):
            self.structured_command += " " + self.variable_name_builder
            self.variable_name_builder = ""

    # This function adds word and append to variable name. E.g. running this on "find", "the", "tree"
    # will result in variable "findTheTree" being built. Subsequently, add_variable_name() must
    # be called to confirm the variable is "findTheTree"
    def append_part_build_var_name(self, word):
        if (word.strip() == ""):
            return
        
        if (self.variable_name_builder == ""):
            self.variable_name_builder = word
        else:
            first_letter = word[0]
            rest_letters = ""
            if (len(word) > 1):
                rest_letters = word[1:]
            # build lower camel case
            self.variable_name_builder += first_letter.upper() + rest_letters

    # Keep reading word and append to variable name until one of the word appears in stop_words list
    def read_variable_name_until_stop_words(self, stop_words):
        while (self.has_next_word()):
            next_word = self.query_next_word()
            if (next_word in stop_words):
                break # stop reading as word is in stop_words list.
            else:
                next_word = self.get_next_word()
                self.append_part_build_var_name(next_word)

    def read_numbers_until_no_more_numbers(self):
        number_builder = "";
        while (self.has_next_word()):
            next_word = self.query_next_word()
            if (next_word in self.number_list):
                next_word = self.get_next_word()
                number_builder += " " + next_word
            else:
                break # stop reading as word is not a number.

        return str(number_builder)

    def query_latest_added_word(self):
        if (self.structured_command != ""):
            parts = self.structured_command.split(" ")
            return parts[len(parts) - 1]

    def ignore_until_stop_words(self, stop_words):
        while (self.has_next_word()):
            next_word = self.query_next_word()
            if (next_word in stop_words):
                break # stop reading as word is in stop_words list.
            else:
                self.get_next_word() # read and ignore

# Stack class
class Stack:
    FUNCTION_STACK = "Function_Stack"
    FOR_STACK = "For_Stack"
    IF_STACK = "If_Stack"
    ELSE_STACK = "Else_Stack"
                
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if (len(self.stack) > 0):
            return self.stack.pop()
        else:
            return None

    def peek(self):
        if (len(self.stack) > 0):
            return self.stack[len(self.stack) - 1]
        else:
            return None

