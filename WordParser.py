from word2number import w2n # External library to parse words to numbers

class WordParser:
    def __init__(self, words):
        self.structured_command = ""
        self.words_to_parse = words.split(" ")
        self.variable_name_builder = ""
        self.number_list = w2n.american_number_system
        self.begin_stack = Stack()
        self.remove_optional_words()

    def map_word_to_structured_command(self):
        while (self.has_next_word()):
            self.process_mapping()

        self.add_variable_name()

        print "command parsed is : " + self.structured_command + "\n"
        return self.structured_command

    def remove_optional_words(self):
        for word in self.words_to_parse:
            if word.lower() in ["with", "reef", "beef"]:
                self.words_to_parse.remove(word)


##declare integer max equal numbers array index zero
##	declare integer i
##
##	for i equal one i less than length i plus plus begin //
##
##		if numbers array index i greater than max then
##			max equal numbers array index i
##		end if
##	end for
##
##	return max
##end function

########################################################################################


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
                        # TODO
                    else:
                        # error
                        self.structured_command += " #create" + var_type + " #variable"
                        self.add_variable_name()
                        self.structured_command += " #dec_end;;"
                        
                    #self.get_next_word()
                    #self.structured_command += " #parameter_a #dimension 1" + var_type + " #array"
                    # #parameter_a #dimension 1 int #array X
                    # TODO
                    

        ## declare integer array sequence size ten end declare // int sequence [10];

#create int #array #variable X #indexes #value 100 #index_end #dec_end;;
                    pass
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
                                    number_read = self.read_numbers_until_no_more_numbers()
                                    number_parsed = w2n.word_to_num(number_read) # convert word to number
                                    self.structured_command += " #value " + str(number_parsed)
                                    
                                    self.code_block_end_declare()
                                else:
                                    # variable / array
                                    self.read_variable_name_until_stop_words(["array", "end"])

                                    if (self.has_next_word()):
                                        next_word = self.get_next_word()
                                        if (next_word == "array"):
                                            if (self.has_next_word()):
                                                next_word = self.get_next_word()
                                                if (next_word == "index"):
                                                    # variable or number
                                                    if (self.has_next_word()):
                                                        self.structured_command += " #array "
                                                        self.add_variable_name()
                                                        self.structured_command += " #indexes "
                                                        
                                                        next_word = self.query_next_word()
                                                        if (next_word in self.number_list):
                                                            # number
                                                            number_read = self.read_numbers_until_no_more_numbers()
                                                            number_parsed = w2n.word_to_num(number_read) # convert word to number
                                                            self.structured_command += " #value " + str(number_parsed)

                                                            self.code_block_end_declare()
                                                        else:
                                                            # variable
                                                            self.read_variable_name_until_stop_words(["end"])
                                                            self.structured_command += " #variable "
                                                            self.add_variable_name()

                                                            self.code_block_end_declare()
                                                    else:
                                                        self.handle_error_assign_variable_when_declaring()
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
                else:
                    pass # unknown word to parse
            else:
                pass # unknown word to parse
        elif (word == "with" or word == "beef" or word == "reef"):
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
                    # return variable / number (to be parsed in next pass)
                    pass
            else:
                self.add_variable_name()
                self.structured_command += " return ;;"
        elif (word == "parameter"):
            self.add_variable_name()
            self.process_parameter()
        elif (word == "begin"):
            self.add_variable_name()
            self.process_begin()
        elif (word == "declare"):
            self.add_variable_name()
            self.process_var_declaration()
            
        else: # variable name
            self.append_part_build_var_name(word)


    def code_block_end_declare(self):
        # End declare
        if (self.has_next_word()):
            next_word = self.get_next_word()
            if (next_word == "end"):
                self.process_end_declare()
            else:
                self.structured_command += " #dec_end;;" # error input
        else:
            self.structured_command += " #dec_end;;" # error input


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

        return number_builder

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
        
x = WordParser("create function find maximum with return type integer with parameter integer array numbers with parameter integer length begin" + \
               " declare integer max equal numbers array index zero end declare declare integer i end declare")
x.map_word_to_structured_command()
