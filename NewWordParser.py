import re
from word2number import w2n # External library to parse words to numbers
from pyparsing import * # External parser library

class WordParser:
    ## This function returns the following: 
    ## ~Keyword("equal") + ~Keyword("end equal") + ~Keyword("array")
    ## if given list @param: all_the_keywords ["equal", "end equal", "array"]
    ## in a form for pyparsing to work on.
    def build_not_all_keywords(self, all_the_keywords):
        temp_not_all_keywords = None
        
        for keyword in all_the_keywords:
            if temp_not_all_keywords is None:
                temp_not_all_keywords = ~Keyword(keyword)
            else:
                temp_not_all_keywords += ~Keyword(keyword)

        return temp_not_all_keywords

    def get_all_literal(self):
        # All the numeric words
        temp_num = ""
        for word in w2n.american_number_system:
            temp_num += " " + word
        temp_num += " and"
        literal = oneOf(temp_num)

        return literal


    def trim_all_spaces(self, words):
        word = ' '.join(str(words).split())
        word = word.strip()

        return word


    def is_literal(self, words):
        words = self.trim_all_spaces(words)
        literal_regex = self.trim_all_spaces(self.literal)
        
        literal_list = literal_regex.split(" | ")
        
        parts = words.split()
        for part in parts:
            if part not in literal_list:
                return False

        return True            


    ## This function transform @param: words into lower camel case variable name.
    ## E.g. running this on "find the tree" will return the string "findTheTree"
    def build_var_name(self, words):
        processed_words = ' '.join(words.split()) # replace multiple spaces with one space

        if processed_words == "" or processed_words == " ":
            return

        word_list = processed_words.split()

        final_var_name = word_list[0]
        
        if (len(word_list) > 1):
            rest_words = word_list[1:]
            # build lower camel case
            for word in rest_words:
                first_letter = word[0]
                rest_letters = ""
                if len(word) > 1:
                    rest_letters = word[1:]

                final_var_name += first_letter.upper() + rest_letters
        return final_var_name


    
    def process_variable_or_literal(self, word, special_syntax_if_var = None):
        if self.is_literal(word):
            return " #value " + str(w2n.word_to_num(word))
        else:
            if special_syntax_if_var == None:
                return " #variable " + self.build_var_name(word)
            else:
                return " " + special_syntax_if_var + " " + self.build_var_name(word)


    def process_var_or_arr_or_literal(self, word):
        operator_regex = "\+|\-|\*|\/|\%"
        parts = re.split(operator_regex, word)

        # Recursively handles cases where there are operators within the variable / literal
        if len(parts) != 1:
            location_operator = re.search(operator_regex, word).start() # find first operator
            front_part_expr = word[:location_operator]
            operator_expr = word[location_operator]
            back_part_expr = word[location_operator + 1:]

            return self.process_var_or_arr_or_literal(front_part_expr) + " " + operator_expr + " " + \
                   self.process_var_or_arr_or_literal(back_part_expr)
        
        try:
            # Test if word is an array
            tokens = self.array_index_phrase.parseString(word)

            # array
            return "#array " + self.build_var_name(tokens[0]) + " #indexes " + self.process_variable_or_literal(tokens[1]) + \
                   " #index_end"
        except ParseException: # no match: not an array
            return self.process_variable_or_literal(word)


    ## This is for setting parse action to output array tags
    def update_array_tags(self, tokens):
        return " #array " + tokens.varname + " #index " + tokens.index


    def update_comparison_ops(self, tokens):        
        if tokens.gt != "": # greater than operation
            return " > "
        elif tokens.ge != "": # greater than equal operation
            return " >= "
        elif tokens.lt != "":
            return " < "
        elif tokens.le != "":
            return " <= "
        elif tokens.ne != "":
            return " != "
        elif tokens.eq != "":
            return " == "
        else:
            # Code should not reach here
            return " unknown "


    def update_operators(self, tokens):
        if tokens.p != "": # plus
            return " + "
        elif tokens.min != "": # minus
            return " - "
        elif tokens.mod != "": # modulo
            return " % "
        elif tokens.t != "": # times
            return " * "
        elif tokens.d != "": # divide
            return" / "
        else:
            # Code should not reach here
            return " unknown "

    def update_end_constructs(self, tokens):
        if tokens.endif != "": # end if operation
            if_or_else = self.if_cond_stack.pop()
            if if_or_else == Stack.IF_STACK:
                return "#if_branch_end"
            elif if_or_else == Stack.ELSE_STACK:
                return "#else_branch_end"
            else: # unknown end if meet
                return " unknown "
        elif tokens.endforloop != "": # end for loop
            return "#for_end"
        else:
            # Code should not reach here
            return " unknown "

    def update_increment_for_operator(self, tokens):
        if tokens.pp != "": # plus plus operation
            return "++"
        elif tokens.mm != "": # minus minus operation
            return "--"
        else: # should not reach here
            return " unknown "

    def update_join_tokens(self, tokens):
        return ' '.join(tokens)


    def retrieve_additional_unparsed(self):
        return self.additional_unparsed_data


    def set_additional_unparsed(self, unparsed_data):
        self.additional_unparsed_data = unparsed_data


    def reinit(self):
        self.additional_unparsed_data = ""
        self.if_cond_stack = Stack()
        
        
    def __init__(self):
        # Some stored variables
        self.additional_unparsed_data = ""
        self.if_cond_stack = Stack()
        
        # Define all keywords here
        keyword_equal = Suppress("equal")
        keyword_end_equal = Suppress("end equal")
        keyword_array_index = Suppress("array index")
        keyword_if = Suppress("if")
        keyword_ns_greater_than = Keyword("greater than")
        keyword_ns_greater_than_equal = Keyword("greater than equal")
        keyword_ns_less_than = Keyword("less than")
        keyword_ns_less_than_equal = Keyword("less than equal")
        keyword_ns_not_equal = Keyword("not equal")
        keyword_ns_equal = Keyword("equal")
        keyword_then = Suppress("then")
        keyword_else = Suppress("else")
        keyword_ns_end_if = Keyword("end if")
        keyword_for = Suppress("for")
        keyword_loop = Suppress("loop")
        keyword_ns_end_for_loop = Keyword("end for") + Optional(keyword_loop)
        keyword_condition = Suppress("condition")
        keyword_begin = Suppress("begin")
        keyword_ns_plus_plus = Keyword("plus plus")
        keyword_ns_minus_minus = Keyword("minus minus")
        keyword_ns_plus = Keyword("plus")
        keyword_ns_minus = Keyword("minus")
        keyword_ns_times = Keyword("times")
        keyword_ns_divide = Keyword("divide")
        keyword_ns_modulo = Keyword("modulo")

        # The list of required keywords
        list_keywords = ["equal", "end equal", "array index", "if", "greater than", "greater than equal"]
        list_keywords += ["less than", "less than equal", "not equal", "then", "else", "end if", "for", "loop"]
        list_keywords += ["condition", "begin", "plus", "minus"]

        # The components of parser
        not_all_keywords = self.build_not_all_keywords(list_keywords)
        self.literal = self.get_all_literal()
        
        variable_name = Combine(ZeroOrMore(not_all_keywords + Word(alphas) + " "))
        literal_name = OneOrMore(self.literal)
        variable_or_literal = variable_name | literal_name

        for_loop = keyword_for + Optional(keyword_loop)

        comparison_operator = keyword_ns_greater_than_equal("ge") | keyword_ns_greater_than("gt") | keyword_ns_less_than_equal("le") \
                              | keyword_ns_less_than("lt") | keyword_ns_not_equal("ne") | keyword_ns_equal("eq")
        comparison_operator.setParseAction(self.update_comparison_ops) # Additional processing for output

        end_constructs = keyword_ns_end_if("endif") | keyword_ns_end_for_loop("endforloop") # todo
        end_constructs.setParseAction(self.update_end_constructs)

        increment_for_operator = keyword_ns_plus_plus("pp") | keyword_ns_minus_minus("mm")
        increment_for_operator.setParseAction(self.update_increment_for_operator)

        operators = keyword_ns_plus("p") |  keyword_ns_minus("min") | keyword_ns_times("t") | \
                    keyword_ns_divide("d") | keyword_ns_modulo("mod")
        operators.setParseAction(self.update_operators)

        variable_with_array_index = variable_name("varname") + keyword_array_index + variable_or_literal("index")
        variable_with_array_index.setParseAction(self.update_array_tags)

        self.array_index_phrase = Suppress("#array") + variable_name + Suppress("#index") + variable_or_literal

        variable_or_variable_with_array_index = variable_with_array_index | variable_name

        var_optional_array_index_or_literal = variable_or_variable_with_array_index | literal_name
        
        var_optional_array_index_or_literal_recur = Forward() # allows for recursion
        var_optional_array_index_or_literal_recur << var_optional_array_index_or_literal + ZeroOrMore(operators + var_optional_array_index_or_literal_recur)
        var_optional_array_index_or_literal_recur.setParseAction(self.update_join_tokens)


        # Constructs parsable
        self.assign_var_stmt = var_optional_array_index_or_literal + keyword_equal + var_optional_array_index_or_literal_recur + keyword_end_equal + restOfLine
        self.if_stmt = keyword_if + var_optional_array_index_or_literal_recur + comparison_operator + var_optional_array_index_or_literal_recur + keyword_then + restOfLine
        self.else_stmt = keyword_else + restOfLine
        self.end_stmt = end_constructs + restOfLine
        self.for_loop_stmt = for_loop + keyword_condition + var_optional_array_index_or_literal + keyword_equal + \
                             var_optional_array_index_or_literal_recur + keyword_condition + var_optional_array_index_or_literal_recur + \
                             comparison_operator + var_optional_array_index_or_literal_recur + keyword_condition + \
                             variable_or_variable_with_array_index + increment_for_operator + keyword_begin + restOfLine
        
 
    def parse(self, sentence):
        if sentence == "":
            return ""
        # Run parsing through each construct

        # Check variable assignment
        result = self.parse_check_variable_assignment(sentence)

        if result["has_match"]:
            return self.trim_all_spaces(result["struct_cmd"]) + " " + self.parse(result["additional_input"])

        # Check if condition
        result = self.parse_check_if_condition(sentence)
        if result["has_match"]:
            self.if_cond_stack.push(Stack.IF_STACK)
            return self.trim_all_spaces(result["struct_cmd"]) + " " + self.parse(result["additional_input"])

        # Check else
        result = self.parse_check_else(sentence)
        if result["has_match"]:
            self.if_cond_stack.pop() # remove "if" from stack
            self.if_cond_stack.push(Stack.ELSE_STACK)

            return self.trim_all_spaces(result["struct_cmd"]) + " " + self.parse(result["additional_input"])

        # Check end constructs
        result  = self.parse_end_constructs(sentence)
        if result["has_match"]:
            return self.trim_all_spaces(result["struct_cmd"]) + " " + self.parse(result["additional_input"])

        # Check for loop
        result = self.parse_check_for_loop(sentence)
        if result["has_match"]:
            return self.trim_all_spaces(result["struct_cmd"]) + " " + self.parse(result["additional_input"])
        

        # No more matches: (unknown data), we stop parsing
        self.set_additional_unparsed(sentence)
        return ""
        

    def parse_check_variable_assignment(self, sentence):
        return_struct = {}

        try:
            list_match_tokens = self.assign_var_stmt.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = "#assign " + self.process_var_or_arr_or_literal(list_match_tokens[0]) + " #with " + \
                    self.process_var_or_arr_or_literal(list_match_tokens[1]) + ";; "
            return_struct["additional_input"] = list_match_tokens[2]
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_if_condition(self, sentence):
        return_struct = {}

        try:
            list_match_tokens = self.if_stmt.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = "if #condition " + self.process_var_or_arr_or_literal(list_match_tokens[0]) + \
                    " " + list_match_tokens[1] + self.process_var_or_arr_or_literal(list_match_tokens[2]) + \
                    " #if_branch_start "
            return_struct["additional_input"] = list_match_tokens[3]
            
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_for_loop(self, sentence):
        return_struct = {}

        try:
            list_match_tokens = self.for_loop_stmt.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = "for #condition #assign " + self.process_var_or_arr_or_literal(list_match_tokens[0]) + \
                    " #with " + self.process_var_or_arr_or_literal(list_match_tokens[1]) + " #condition " + \
                    self.process_var_or_arr_or_literal(list_match_tokens[2]) + " " + list_match_tokens[3] +  " " + \
                    self.process_var_or_arr_or_literal(list_match_tokens[4]) + " #condition #post " + \
                    self.process_var_or_arr_or_literal(list_match_tokens[5]) + " " + list_match_tokens[6] + " #for_start"
            return_struct["additional_input"] = list_match_tokens[7]
            
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_else(self, sentence):
        return_struct = {}

        try:
            list_match_tokens = self.else_stmt.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = " #if_branch_end #else_branch_start "
            return_struct["additional_input"] = list_match_tokens[0]
            
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_end_constructs(self, sentence):
        return_struct = {}

        try:
            list_match_tokens = self.end_stmt.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_match_tokens[0] + ";; "
            return_struct["additional_input"] = list_match_tokens[1]
            
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


# Stack class
class Stack:
    FUNCTION_STACK = "Function_Stack"
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


if __name__ == "__main__":
    def compare(word1, word2, wp):
        return wp.trim_all_spaces(wp.parse(word1)) == wp.trim_all_spaces(word2) 
        

    wordParser = WordParser()

    # Some quick hack unit tests
    speech = "max two equal numbers array index i end equal"
    struct = "#assign #variable maxTwo #with #array numbers #indexes #variable i #index_end;;"
    print compare(speech, struct, wordParser)

    speech = "max equal numbers hello array index two end equal"
    struct = "#assign #variable max #with #array numbersHello #indexes #value 2 #index_end;;"
    print compare(speech, struct, wordParser)

    speech = "max equal one hundred and twenty two end equal"
    struct = "#assign #variable max #with #value 122;;"
    print compare(speech, struct, wordParser)

    speech = "max equal min end equal"
    struct = "#assign #variable max #with #variable min;;"
    print compare(speech, struct, wordParser)

    speech = "max three array index i equal min end equal"
    struct = "#assign #array maxThree #indexes #variable i #index_end #with #variable min;;"
    print compare(speech, struct, wordParser)
    
    speech = "max array index twenty one equal min end equal"
    struct = "#assign #array max #indexes #value 21 #index_end #with #variable min;;"
    print compare(speech, struct, wordParser)

    speech = "if numbers array index i greater than max then"
    struct = "if #condition #array numbers #indexes #variable i #index_end > #variable max #if_branch_start"
    print compare(speech, struct, wordParser)

    speech = "if numbers array index i less than max then"
    struct = "if #condition #array numbers #indexes #variable i #index_end < #variable max #if_branch_start"
    print compare(speech, struct, wordParser)

    speech = "if numbers array index i greater than equal max then"
    struct = "if #condition #array numbers #indexes #variable i #index_end >= #variable max #if_branch_start"
    print compare(speech, struct, wordParser)

    speech = "if numbers array index i less than equal max then"
    struct = "if #condition #array numbers #indexes #variable i #index_end <= #variable max #if_branch_start"
    print compare(speech, struct, wordParser)

    speech = "if numbers array index i equal max then"
    struct = "if #condition #array numbers #indexes #variable i #index_end == #variable max #if_branch_start"
    print compare(speech, struct, wordParser)

    speech = "if numbers array index i not equal max then"
    struct = "if #condition #array numbers #indexes #variable i #index_end != #variable max #if_branch_start"
    print compare(speech, struct, wordParser)
          
    wordParser.reinit()
    speech = "if max equal min then max equal one end equal else max equal two end equal end if"
    struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
    print compare(speech, struct, wordParser)

    wordParser.reinit()
    speech = "if numbers array index i greater than max then end if"
    struct = "if #condition #array  numbers #indexes  #variable  i #index_end > #variable max #if_branch_start #if_branch_end;; "
    print compare(speech, struct, wordParser)

    speech = "for loop condition i equal one condition i less than length condition i plus plus begin end for loop"
    struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ #for_start #for_end;;"
    print compare(speech, struct, wordParser)
    
    speech = "max equal numbers array index i plus min plus twenty end equal"
    struct = "#assign #variable max #with #array numbers #indexes #variable i #index_end + #variable min + #value 20;; "
    print compare(speech, struct, wordParser)

    speech = "for loop condition i equal one condition i plus two less than length condition i plus plus begin end for loop"
    struct = "for #condition #assign #variable i #with #value 1 #condition #variable i + #value 2 < #variable length #condition #post #variable i ++ #for_start #for_end;;"
    print compare(speech, struct, wordParser)

    wordParser.reinit()
    speech = "if i plus j plus k greater than max then end if"
    struct = "if #condition #variable i + #variable j + #variable k > #variable max #if_branch_start #if_branch_end;; "
    print compare(speech, struct, wordParser)
    

