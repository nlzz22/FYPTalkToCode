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
        if words.strip() == "":
            return False
        
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
        if word.strip() == "":
            return ""
        
        if self.is_literal(word):
            return " #value " + str(w2n.word_to_num(word))
        else:
            try:
                # if word is already in number form
                float(word)

                return " #value " + str(word)
            except ValueError:
                if special_syntax_if_var == None:
                    return " #variable " + self.build_var_name(word)
                else:
                    return " " + special_syntax_if_var + " " + self.build_var_name(word)
                

    def parse_var_arr_or_literal(self, toks):
        word = toks[0]

        try:
            # Test if word is an array
            tokens = self.array_index_phrase.parseString(word)

            # array
            return "#array " + " " + self.build_var_name(tokens[0]) + " #indexes " + \
                   self.process_variable_or_literal(tokens[1]) + " #index_end"
        except ParseException: # no match: not an array
            return self.process_variable_or_literal(word)


    def parse_var_arr_or_literal_word(self, word):
        return self.parse_var_arr_or_literal([word])
    

    def parse_arr_with_size(self, toks):
        var_name = toks[0]
        size = toks[1]

        return "#variable " + var_name + " #indexes " + self.process_variable_or_literal(size) + " #index_end"


    ## This is for setting parse action to output array tags
    def update_array_tags(self, tokens):
        return " #array " + tokens.varname + " #index " + tokens.index


    ## This is for setting parse action to output parameter tags
    def update_parameter_arguments(self, tokens):
        var_or_array = tokens.varname
        var_type = tokens.vartype

        try:
            # Test if it is an array
            inner_tokens = self.array_variable_phrase.parseString(var_or_array)

            return " #parameter_a #dimension 1 " + var_type + " #array " + self.build_var_name(inner_tokens[0])
        except ParseException: # no match: not an array, but a variable
            return " #parameter " + var_type + self.build_var_name(var_or_array)


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


    def update_var_type(self, tokens):
        if tokens.int != "": # integer
            return " int "
        elif tokens.float != "": # float
            return " float "
        elif tokens.double != "": # double
            return " double "
        elif tokens.long != "": # long
            return " long "
        elif tokens.void != "": # void
            return " void "
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


    def parse_assignment_statement(self, tokens):
        return "#assign " + tokens[0] + " #with " + tokens[1] + ";; "


    def parse_if_statement(self, tokens):
        # tokens consist of [ expression, comparison_operator, expression, statements (multiple) ]
        parsed_stmt = "if #condition " + tokens[0] + " " + tokens[1] + " " + tokens[2] + " #if_branch_start "

        for i in range(3, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += "#if_branch_end;;"
            
        return parsed_stmt


    def parse_if_else_statement(self, tokens):
        # tokens consist of [ expression, comparison_operator, expression, statements (multiple) ]
        # statements are split into ifclause statements and elseclause statements
        parsed_stmt = "if #condition " + tokens[0] + " " + tokens[1] + " " + tokens[2] + " #if_branch_start "

        for i in range(0, len(tokens.ifclause)):
            parsed_stmt += tokens.ifclause[i] + " "

        parsed_stmt += "#if_branch_end #else_branch_start "

        for j in range(0, len(tokens.elseclause)):
            parsed_stmt += tokens.elseclause[j] + " "

        parsed_stmt += "#else_branch_end;;"
            
        return parsed_stmt


    def parse_for_loop_statement(self, tokens):
        # tokens consist of [ var_arr_literal, expression, expression, comparison_operator, expression, var_arr, increment_for_op,
        # statements (multiple)]
        parsed_stmt = "for #condition #assign " + tokens[0] + " #with " + tokens[1] + " #condition " + tokens[2] + " " + \
                      tokens[3] + " " + tokens[4] + " #condition #post " + self.parse_var_arr_or_literal_word(tokens[5]) + \
                      " "  + tokens[6] + " #for_start "

        for i in range(7, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += "#for_end;;"

        return parsed_stmt


    def parse_function_declaration(self, tokens):
        # tokens consist of [ var_name, var_type, parameter_statements (multiple) + statement (multiple) ]
        # statements are tokens.stmts and parameter_statements are token.params
        parsed_stmt = "#function_declare " + self.build_var_name(tokens[0]) + " " + tokens[1]
        
        for i in range(0, len(tokens.params)):
            parsed_stmt += tokens.params[i]
            
        parsed_stmt += " #function_start "

        for j in range(0, len(tokens.stmts)):
            parsed_stmt += tokens.stmts[j] + " "

        parsed_stmt += "#function_end;;"

        return parsed_stmt


    def parse_declare_var_statement(self, tokens):
        # tokens consist of [ variable_type, variable_name, optional (expression) ]
        parsed_stmt = "#create " + tokens[0] + " " + tokens[1]
        if len(tokens) == 3:
            parsed_stmt += " " + tokens[2]
        parsed_stmt += " #dec_end;;"

        return parsed_stmt

    def parse_declare_arr_statement(self, tokens):
        # tokens consist of [ variable_type, variable_name_with_size ] 
        return "#create " + tokens[0] + " #array " + tokens[1] + " #dec_end;;"

    def parse_return_statement(self, tokens):
        # tokens consist of [ expression ]
        return "return " + tokens[0] + ";;"
        
        
    def __init__(self):        
        # Define all keywords here
        keyword_equal = Suppress("equal")
        keyword_end_equal = Suppress("end equal")
        keyword_array = Suppress("array")
        keyword_array_index = Suppress("array index")
        keyword_if = Suppress("begin if")
        keyword_ns_greater_than = Keyword("greater than")
        keyword_ns_greater_than_equal = Keyword("greater than equal")
        keyword_ns_less_than = Keyword("less than")
        keyword_ns_less_than_equal = Keyword("less than equal")
        keyword_ns_not_equal = Keyword("not equal")
        keyword_ns_equal = Keyword("equal")
        keyword_then = Suppress("then")
        keyword_else = Suppress("else")
        keyword_end_if = Suppress("end if")
        keyword_for = Suppress("for")
        keyword_loop = Suppress("loop")
        keyword_end_for_loop = Suppress("end for") + Optional(keyword_loop)
        keyword_condition = Suppress("condition")
        keyword_begin = Suppress("begin")
        keyword_ns_plus_plus = Keyword("plus plus")
        keyword_ns_minus_minus = Keyword("minus minus")
        keyword_ns_plus = Keyword("plus")
        keyword_ns_minus = Keyword("minus")
        keyword_ns_times = Keyword("times")
        keyword_ns_divide = Keyword("divide")
        keyword_ns_modulo = Keyword("modulo")
        keyword_declare = Suppress("declare")
        keyword_ns_integer = Keyword("integer")
        keyword_ns_float = Keyword("float")
        keyword_ns_double = Keyword("double")
        keyword_ns_long = Keyword("long")
        keyword_ns_void = Keyword("void")
        keyword_end_declare = Suppress("end declare")
        keyword_with = Suppress("with")
        keyword_size = Suppress("size")
        keyword_return = Suppress("return")
        keyword_create_function = Suppress("create function")
        keyword_return_type = Suppress("return type")
        keyword_parameter = Suppress("parameter")
        keyword_end_function = Suppress("end function")

        # The list of required keywords
        list_keywords = ["equal", "end equal", "array index", "begin if", "greater than", "greater than equal"]
        list_keywords += ["less than", "less than equal", "not equal", "then", "else", "end if", "for", "loop"]
        list_keywords += ["condition", "begin", "plus", "minus", "declare", "integer", "float", "double", "long"]
        list_keywords += ["end for", "times", "divide", "modulo", "end declare", "array", "with", "size", "return"]
        list_keywords += ["void", "create function", "return type", "parameter", "end function"]

        # The components of parser
        not_all_keywords = self.build_not_all_keywords(list_keywords)
        self.literal = self.get_all_literal() 
        
        variable_name = Combine(OneOrMore(not_all_keywords + Word(alphas) + Optional(" ")))
        literal_name = OneOrMore(self.literal)
        variable_or_literal = variable_name | literal_name

        # This function cannot use variable_name or it will ruin other functions due to the pre-formatting.
        variable_name_processed = Combine(OneOrMore(not_all_keywords + Word(alphas) + Optional(" ")))
        variable_name_processed.setParseAction(self.parse_var_arr_or_literal)

        for_loop = keyword_for + Optional(keyword_loop)

        comparison_operator = keyword_ns_greater_than_equal("ge") | keyword_ns_greater_than("gt") | keyword_ns_less_than_equal("le") \
                              | keyword_ns_less_than("lt") | keyword_ns_not_equal("ne") | keyword_ns_equal("eq")
        comparison_operator.setParseAction(self.update_comparison_ops) # Additional processing for output

        variable_type = keyword_ns_integer("int") | keyword_ns_float("float") | keyword_ns_double("double") | keyword_ns_long("long") | \
                        keyword_ns_void("void") # todo
        variable_type.setParseAction(self.update_var_type)

        increment_for_operator = keyword_ns_plus_plus("pp") | keyword_ns_minus_minus("mm")
        increment_for_operator.setParseAction(self.update_increment_for_operator)

        operators = keyword_ns_plus("p") |  keyword_ns_minus("min") | keyword_ns_times("t") | \
                    keyword_ns_divide("d") | keyword_ns_modulo("mod")
        operators.setParseAction(self.update_operators)

        assignment_operator = keyword_equal

        variable_with_array_index = variable_name("varname") + keyword_array_index + variable_or_literal("index")
        variable_with_array_index.setParseAction(self.update_array_tags)

        variable_with_size_index = variable_name("varname") + Optional(keyword_with) + keyword_size + variable_or_literal("index")
        variable_with_size_index.setParseAction(self.update_array_tags)
        variable_with_size = variable_with_size_index
        variable_with_size.setParseAction(self.parse_arr_with_size)

        self.array_index_phrase = Suppress("#array") + variable_name + Suppress("#index") + variable_or_literal
        self.array_variable_phrase = keyword_array + variable_name

        variable_or_variable_with_array_index = variable_with_array_index | variable_name

        variable_or_array = (Keyword("array") + variable_name) | variable_name
        variable_or_array.setParseAction(self.update_join_tokens)
        parameter_statement = Optional(keyword_with) + keyword_parameter + variable_type("vartype") + variable_or_array("varname")
        parameter_statement.setParseAction(self.update_parameter_arguments)

        var_arr_or_literal = variable_or_variable_with_array_index | literal_name
        var_arr_or_literal.setParseAction(self.parse_var_arr_or_literal) # add in #array, #value or #variable      

        statement = Forward()

        mathematical_expression = Forward()
        mathematical_expression << var_arr_or_literal + ZeroOrMore(operators + mathematical_expression)
        mathematical_expression.setParseAction(self.update_join_tokens) # join completed var/arr/literal with operators

        expression = mathematical_expression

        if_statement = keyword_if + expression + comparison_operator + expression + keyword_then + ZeroOrMore(statement) + \
                           keyword_end_if
        if_statement.setParseAction(self.parse_if_statement)

        if_else_statement = keyword_if + expression + comparison_operator + expression + keyword_then + ZeroOrMore(statement.setResultsName("ifclause", True)) + \
                             keyword_else + ZeroOrMore(statement.setResultsName("elseclause", True)) + keyword_end_if
        if_else_statement.setParseAction(self.parse_if_else_statement)

        declare_variable_statement = keyword_declare + variable_type + variable_name_processed + Optional(assignment_operator + expression) + \
                                keyword_end_declare
        declare_variable_statement.setParseAction(self.parse_declare_var_statement)

        declare_array_statement = keyword_declare + variable_type + keyword_array + variable_with_size + \
                                  keyword_end_declare
        declare_array_statement.setParseAction(self.parse_declare_arr_statement)

        for_loop_statement = for_loop + keyword_condition + var_arr_or_literal + keyword_equal + expression + \
                             keyword_condition + expression + comparison_operator + expression + \
                             keyword_condition + variable_or_variable_with_array_index + increment_for_operator + keyword_begin + \
                             ZeroOrMore(statement) + keyword_end_for_loop
        for_loop_statement.setParseAction(self.parse_for_loop_statement)

        return_statement = keyword_return + expression
        return_statement.setParseAction(self.parse_return_statement)

        # Constructs parsable
        self.assignment_statement = var_arr_or_literal + assignment_operator + expression + keyword_end_equal
        self.assignment_statement.setParseAction(self.parse_assignment_statement)

        self.selection_statement = if_statement | if_else_statement

        self.declaration_statement = declare_variable_statement | declare_array_statement

        self.iteration_statement = for_loop_statement

        self.jump_statement = return_statement

        statement << (self.assignment_statement | self.selection_statement | self.declaration_statement | \
                  self.iteration_statement | self.jump_statement)

        self.function_declaration = keyword_create_function + variable_name + Optional(keyword_with) + keyword_return_type + \
                               variable_type + ZeroOrMore(parameter_statement.setResultsName("params", True)) + keyword_begin + \
                               ZeroOrMore(statement.setResultsName("stmts", True)) + keyword_end_function
        self.function_declaration.setParseAction(self.parse_function_declaration)
        
 
    def parse(self, sentence):
        sentence = str(sentence).lower()
        
        if sentence == "":
            return ""

        words = sentence.split()
        if len(words) < 2:
            return ""

        first_word = words[0]
        start_word = words[0] + " " + words[1]

        # Check selection statements
        if start_word == "begin if":
            result = self.parse_check_selection_statement(sentence)
        # Check declaration statements
        elif first_word == "declare":
            result = self.parse_check_declaration_statement(sentence)
        # Check iteration statements
        elif first_word == "for":
            result = self.parse_check_iteration_statement(sentence)
        # Check jump statements
        elif first_word == "return":
            result = self.parse_check_jump_statement(sentence)
        # Check function declaration
        elif start_word == "create function":
            result = self.parse_check_function_declaration(sentence)
        # Else, assume variable assignment check
        else:
            result = self.parse_check_variable_assignment(sentence)

        if result["has_match"]:
            return self.trim_all_spaces(result["struct_cmd"])
        else:
            # no matches
            return ""
        

    def parse_check_variable_assignment(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.assignment_statement.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_parsed[0]
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_selection_statement(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.selection_statement.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_parsed[0]
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_iteration_statement(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.iteration_statement.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_parsed[0]
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_declaration_statement(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.declaration_statement.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_parsed[0]
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_jump_statement(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.jump_statement.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_parsed[0]
        except ParseException:
            return_struct["has_match"] = False

        return return_struct


    def parse_check_function_declaration(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.function_declaration.parseString(sentence)
            
            return_struct["has_match"] = True
            return_struct["struct_cmd"] = list_parsed[0]            
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
        if (wp.trim_all_spaces(wp.parse(word1)) == wp.trim_all_spaces(word2)):
            return "."
        else:
            print "Compare results wrong! "
            print word1
            print "----"
            print wp.trim_all_spaces(wp.parse(word1))
            print "----"
            print wp.trim_all_spaces(word2)
            return "WHY YOU WRONG :("
        

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

    speech = "begin if a greater than b then a equal b end equal c equal d end equal end if"
    struct = "if #condition #variable a > #variable b #if_branch_start #assign #variable a #with #variable b;; #assign #variable c #with #variable d;; #if_branch_end;;"
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i greater than max then end if"
    struct = "if #condition #array numbers #indexes #variable i #index_end > #variable max #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i less than max then end if"
    struct = "if #condition #array numbers #indexes #variable i #index_end < #variable max #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i greater than equal max then end if"
    struct = "if #condition #array numbers #indexes #variable i #index_end >= #variable max #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i less than equal max then end if"
    struct = "if #condition #array numbers #indexes #variable i #index_end <= #variable max #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i equal max then end if"
    struct = "if #condition #array numbers #indexes #variable i #index_end == #variable max #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i not equal max then end if"
    struct = "if #condition #array numbers #indexes #variable i #index_end != #variable max #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)
          
    speech = "begin if max equal min then max equal one end equal else max equal two end equal end if"
    struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
    print compare(speech, struct, wordParser)

    speech = "begin if max equal min then max equal one end equal  a equal b end equal else max equal two end equal end if"
    struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #assign #variable a #with #variable b;; #if_branch_end #else_branch_start #assign #variable max #with #value 2;; #else_branch_end;; "
    print compare(speech, struct, wordParser)

    speech = "begin if max equal min then max equal one end equal else a equal b end equal max equal two end equal end if"
    struct = "if #condition #variable max == #variable min #if_branch_start #assign #variable max #with #value 1;; #if_branch_end #else_branch_start #assign #variable a #with #variable b;; #assign #variable max #with #value 2;; #else_branch_end;; "
    print compare(speech, struct, wordParser)

    speech = "begin if numbers array index i greater than max then end if"
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

    speech = "begin if i plus j plus k greater than max then end if"
    struct = "if #condition #variable i + #variable j + #variable k > #variable max #if_branch_start #if_branch_end;; "
    print compare(speech, struct, wordParser)

    speech = "declare integer max equal numbers array index zero end declare "
    struct = "#create int #variable max #array numbers #indexes  #value 0 #index_end #dec_end;; "
    print compare(speech, struct, wordParser)

    speech = "declare integer i end declare"
    struct = "#create int #variable i #dec_end;; "
    print compare(speech, struct, wordParser)

    speech = "declare integer i equal j plus one end declare"
    struct = "#create int #variable i #variable j + #value 1 #dec_end;; "
    print compare(speech, struct, wordParser)

    speech = "declare integer array sequence with size ten end declare"
    struct = "#create int #array #variable sequence #indexes #value 10 #index_end #dec_end;;"    
    print compare(speech, struct, wordParser)
    
    speech = "declare integer array sequence with size amount end declare"
    struct = "#create int #array #variable sequence #indexes #variable amount #index_end #dec_end;;"
    print compare(speech, struct, wordParser)

    speech = "declare integer array sequence size amount end declare"
    struct = "#create int #array #variable sequence #indexes #variable amount #index_end #dec_end;;"
    print compare(speech, struct, wordParser)

    speech = "return max"
    struct = "return #variable max;;"
    print compare(speech, struct, wordParser)

    speech = "return zero"
    struct = "return #value 0;;"
    print compare(speech, struct, wordParser)

    speech = "return i plus two"
    struct = "return #variable i + #value 2;;"
    print compare(speech, struct, wordParser)

    speech = "create function find maximum with return type integer with parameter integer array numbers " + \
             "with parameter integer length begin end function"
    struct = "#function_declare findMaximum int #parameter_a #dimension 1 int #array numbers #parameter int length #function_start #function_end;;"
    print compare(speech, struct, wordParser)

    speech = "create function main with return type void begin end function"
    struct = "#function_declare main void #function_start #function_end;;"
    print compare(speech, struct, wordParser)

    speech = "for loop condition i equal one condition i less than length condition i plus plus begin " + \
             "begin if numbers array index i greater than max then " + \
             "max equal numbers array index i end equal " + \
             "end if end for loop "
    struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #variable length #condition #post #variable i ++ " + \
             "#for_start if #condition #array numbers #indexes #variable i #index_end > #variable max #if_branch_start " + \
             "#assign #variable max #with #array numbers #indexes #variable i #index_end;; #if_branch_end;; #for_end;; "
    print compare(speech, struct, wordParser)

    # Test sample code
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
    print compare(speech, struct, wordParser)
    
