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


    def update_end_constructs(self, tokens):
        if tokens.endif != "": # end if operation
            if_or_else = self.if_cond_stack.pop()
            if if_or_else == Stack.IF_STACK:
                return "#if_branch_end"
            elif if_or_else == Stack.ELSE_STACK:
                return "#else_branch_end"
            else: # unknown end if meet
                return " unknown "
        else:
            # Code should not reach here
            return " unknown "


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

        # The list of required keywords
        list_keywords = ["equal", "end equal", "array index", "if", "greater than", "greater than equal"]
        list_keywords += ["less than", "less than equal", "not equal", "then", "else", "end if"]

        # The components of parser
        not_all_keywords = self.build_not_all_keywords(list_keywords)
        self.literal = self.get_all_literal()
        
        variable_name = Combine(ZeroOrMore(not_all_keywords + Word(alphas) + " "))
        literal_name = OneOrMore(self.literal)
        variable_or_literal = variable_name | literal_name

        comparison_operator = keyword_ns_greater_than_equal("ge") | keyword_ns_greater_than("gt") | keyword_ns_less_than_equal("le") \
                              | keyword_ns_less_than("lt") | keyword_ns_not_equal("ne") | keyword_ns_equal("eq")
        # Additional processing for output
        comparison_operator.setParseAction(self.update_comparison_ops)

        end_constructs = keyword_ns_end_if("endif") # todo
        # Additional processing for output
        end_constructs.setParseAction(self.update_end_constructs)

        variable_with_array_index = variable_name("varname") + keyword_array_index + variable_or_literal("index")
        # Additional processing for output
        variable_with_array_index.setParseAction(self.update_array_tags)

        self.array_index_phrase = Suppress("#array") + variable_name + Suppress("#index") + variable_or_literal

        variable_or_variable_with_array_index = variable_with_array_index | variable_name

        var_optional_array_index_or_literal = variable_or_variable_with_array_index | literal_name

        # Constructs parsable
        self.assign_var_stmt = var_optional_array_index_or_literal + keyword_equal + var_optional_array_index_or_literal + keyword_end_equal + restOfLine
        self.if_stmt = keyword_if + var_optional_array_index_or_literal + comparison_operator + var_optional_array_index_or_literal + keyword_then + restOfLine
        self.else_stmt = keyword_else + restOfLine
        self.end_stmt = end_constructs + restOfLine

        
 
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

