import re
from word2number import w2n # External library to parse words to numbers
from pyparsing import * # External parser library
from Keywords import Keywords

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

        for keyword in self.literal_words:
            temp_not_all_keywords += ~Keyword(keyword)

        return temp_not_all_keywords

    def get_all_literal(self):
        self.literal_words = []
        
        # All the numeric words
        temp_num = ""
        for word in w2n.american_number_system:
            temp_num += " " + word
            self.literal_words.append(word)
        #temp_num += " and"
        #self.literal_words.append("and")
        literal = oneOf(temp_num)

        return literal


    def trim_all_spaces(self, words):
        word = ' '.join(str(words).split())
        word = word.strip()

        return word


    def is_number(self, words):
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
        
        if self.is_number(word): # if is number
            return " #value " + str(w2n.word_to_num(word))
        elif "\"" in word: # if is string
            return " #value " + word[:-2] + "\""
        elif "'" in word: # if is character
            return " #value " + word
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
        var_name = self.build_var_name(toks[0])
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

            variable_name = self.build_var_name(inner_tokens[0])

            # Add to variables list.
            self.add_variable_by_word(variable_name)

            return " #parameter_a #dimension 1 " + var_type + " #array " + variable_name
        except ParseException: # no match: not an array, but a variable
            variable_name = self.build_var_name(var_or_array)

            # Add to variables list.
            self.add_variable_by_word(variable_name)
            
            return " #parameter " + var_type + variable_name


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


    def update_symbol_expr(self, tokens):
        if tokens.amp != "": # ampersand
            return "&"
        elif tokens.dol != "": # dollar
            return "$"
        elif tokens.per != "": # percent
            return "%"
        elif tokens.bac != "": # backslash
            return "\\"
        elif tokens.col != "": # colon
            return ":"
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


    def update_assignment_operators(self, tokens):
        if tokens.eq != "": # equal
            return " #with "
        elif tokens.pe != "": # plus equal
            return " += "
        elif tokens.me != "": # minus equal
            return " -= "
        elif tokens.modeq != "": # modulo equal
            return " %= "
        elif tokens.te != "": # times equal
            return " *= "
        elif tokens.de != "": # divide equal
            return" /= "
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
            return " "
        elif tokens.char != "": # character
            return " char "
        else:
            # Code should not reach here
            return " unknown "
        

    def update_unary_operators(self, tokens):
        if tokens.pp != "": # plus plus operation
            return "++"
        elif tokens.mm != "": # minus minus operation
            return "--"
        else: # should not reach here
            return " unknown "


    def parse_literal(self, tokens):       
        if tokens.charlit != "": # character literal
            return "'" + tokens[0] + "'"
        elif tokens.strlit != "": # string literal
            return "\"" + tokens[0] + "\""
        else: # normal literal (number / floating pt number)
            return tokens
        

    def update_join_tokens(self, tokens):
        return ' '.join(tokens)


    def parse_simple_assign_expression(self, tokens):
        # tokens consist of [ var_or_arr, assignment_operator, expression ]
        return "#assign " + self.parse_var_arr_or_literal_word(tokens[0]) + " " + tokens[1] + " " + tokens[2]


    def parse_postfix_expression(self, tokens):
        # tokens consist of [ var_or_arr, unary_operator ]
        return "#post " + self.parse_var_arr_or_literal_word(tokens[0]) + " " + tokens[1]


    def parse_prefix_expression(self, tokens):
        # tokens consist of [ unary_operator, var_or_arr ]
        return tokens[0] + " " + self.parse_var_arr_or_literal_word(tokens[1])


    def parse_assignment_statement(self, tokens):
        # tokens consist of [ assignment_expression ]
        parsed_stmt = tokens[0] + ";; "
        
        return parsed_stmt


    def parse_if_statement(self, tokens):
        # tokens consist of [ conditional_expression, statements (multiple) ]
        parsed_stmt = "if #condition " + tokens[0] + " #if_branch_start "

        for i in range(1, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += "#if_branch_end;;"
            
        return parsed_stmt


    def parse_if_else_statement(self, tokens):
        # tokens consist of [ conditional_expression, statements (multiple) ]
        # statements are split into ifclause statements and elseclause statements
        parsed_stmt = "if #condition " + tokens[0] + " #if_branch_start "

        for i in range(0, len(tokens.ifclause)):
            parsed_stmt += tokens.ifclause[i] + " "

        parsed_stmt += "#if_branch_end #else_branch_start "

        for j in range(0, len(tokens.elseclause)):
            parsed_stmt += tokens.elseclause[j] + " "

        parsed_stmt += "#else_branch_end;;"
            
        return parsed_stmt


    def parse_for_loop_statement(self, tokens):
        # tokens consist of [ assignment_expression, conditional_expression, assignment_expression,
        # statements (multiple)]
        parsed_stmt = "for #condition " + tokens[0] + " #condition " + tokens[1] + \
                      " #condition " + tokens[2] + " #for_start "

        for i in range(3, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += "#for_end;;"

        return parsed_stmt


    def parse_while_loop_statement(self, tokens):
        # tokens consist of [ conditional_expression, statements (multiple) ]
        parsed_stmt = "while #condition " + tokens[0] + " #while_start "

        for i in range(1, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += " #while_end;;"

        return parsed_stmt


    def parse_function_declaration(self, tokens):
        # tokens consist of [ var_name, var_type, parameter_statements (multiple) + statement (multiple) ]
        # statements are tokens.stmts and parameter_statements are token.params
        function_name = self.build_var_name(tokens[0])

        # add function name to variables list.
        self.add_variable_by_word(function_name)
        
        parsed_stmt = "#function_declare " + function_name + " " + tokens[1]
        
        for i in range(0, len(tokens.params)):
            parsed_stmt += tokens.params[i]
            
        parsed_stmt += " #function_start "

        for j in range(0, len(tokens.stmts)):
            parsed_stmt += tokens.stmts[j] + " "

        parsed_stmt += "#function_end;;"

        return parsed_stmt


    def parse_function_call_statement(self, tokens):
        # tokens consist of [ var_name, parameter_statements (multiple)]
        parsed_stmt = "#function " + self.build_var_name(tokens[0]) + "("
        separator = ""

        for i in range(1, len(tokens)):
            parsed_stmt += separator + "#parameter " + tokens[i]
            separator = " "

        parsed_stmt += ");;"

        return parsed_stmt

    def parse_case_stmt(self, tokens):
        # tokens consist of [ literal_name, statements (multiple)]
        parsed_stmt = " case " + self.process_variable_or_literal(tokens[0]) + " #case_start "

        for i in range(1, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += " #case_end"

        return parsed_stmt

    def parse_default_stmt(self, tokens):
        # tokens consist of [ statements (multiple)]
        parsed_stmt = " default #case_start "

        for i in range(0, len(tokens)):
            parsed_stmt += tokens[i] + " "

        parsed_stmt += " #case_end"

        return parsed_stmt


    def parse_switch_statement(self, tokens):
        # tokens consist of [ conditional_expression, case/default stmts (multiple) ]
        parsed_stmt = " switch #condition " + tokens[0]

        for i in range(1, len(tokens)):
            parsed_stmt += " " + tokens[i]

        parsed_stmt += ";;"

        return parsed_stmt


    def parse_logical_and_cond_expr(self, tokens):
        # tokens consist of [ conditional_expression ]
        parsed_stmt = " && " + tokens[0]
        return parsed_stmt


    def parse_logical_or_cond_expr(self, tokens):
        # tokens consist of [ conditional_expression ]
        parsed_stmt = " || " + tokens[0]
        return parsed_stmt


    # Ensures that expression does not have terminating ;; symbol.
    def parse_expression(self, tokens):
        new_tokens = []
        for token in tokens:
            if len(token) > 1 and token[-2:] == ";;":
                new_tokens.append(token[:-2]) # get string w/o last 2 characters
            else:
                new_tokens.append(token)
        return ' '.join(new_tokens)


    # variable is given in lower camel case form, separates them into individual words and
    # adds individual words to the variables list
    # e.g. findTheTree will add "find", "the", "tree" to the variables_list
    def add_variable_by_word(self, variable):
        variable = variable.replace(" ", "") # remove all spaces
        variable = variable.replace("#variable", "") # remove all #variable word.
        
        has_added = False
            
        for index in range(len(variable)):
            if variable[index].isupper():
                has_added = True
                word_to_add = variable[:index]

                # if part of variable name is NOT a keyword
                if word_to_add not in self.list_keywords and word_to_add not in self.literal_words:
                    # add that to variables list.
                    self.variables.append(variable[:index])
                # recursively try to add the rest of the words.
                self.add_variable_by_word(variable[index].lower() + variable[index + 1:])
                break

        # if variable is a word by itself (e.g. "tree")
        if not has_added:
            self.variables.append(variable)        
        

    def parse_declare_var_statement(self, tokens):
        # tokens consist of [ variable_type, variable_name, optional (expression) ]
        parsed_stmt = "#create " + tokens[0] + " " + tokens[1]
        if len(tokens) == 3:
            parsed_stmt += " " + tokens[2]
        parsed_stmt += " #dec_end;;"

        # add to variables list.
        self.add_variable_by_word(tokens[1])

        return parsed_stmt

    def parse_declare_arr_statement(self, tokens):
        # tokens consist of [ variable_type, variable_name_with_size ]

        # add to variables list.
        extracted_variables = Suppress("#variable") + Word(alphas)
        extracted_variables_list = extracted_variables.searchString(tokens[1])
        for inner_list in extracted_variables_list:
            word = inner_list[0]
            self.add_variable_by_word(word)
        
        return "#create " + tokens[0] + " #array " + tokens[1] + " #dec_end;;"

    def parse_return_statement(self, tokens):
        # tokens consist of [ expression ]
        return "return " + tokens[0] + ";;"

    def parse_break_statement(self, tokens):
        # no tokens here.
        return "break;;"

    def parse_continue_statement(self, tokens):
        # no tokens here.
        return "continue;;"

    def handle_fail_parse(self, string, loc, expr, err):
        if self.error_message != "":
            self.error_message += " or " + str(expr)
        else:
            self.error_message = str(expr)

    def get_error_message(self):
        parts = self.error_message.split(" or ")
        parts = [part.strip() for part in parts]
        
        parts_without_duplicate = set()
        for part in parts:
            parts_without_duplicate.add(part)
        
        parts_without_duplicate = list(parts_without_duplicate)

        error_message = " or ".join(parts_without_duplicate)
        
        return "Expected " + error_message


    def get_variables(self):
        var_list = set()
        for variable in self.variables:
            var_list.add(variable)
        var_list = list(var_list)

        return var_list
            
        
        
    def __init__(self):
        self.error_message = ""
        self.variables = []
        
        # Define all keywords here
        keyword_equal = Suppress("equal")
        #keyword_end_equal = Suppress("end equal").setName("\"end equal\"").setFailAction(self.handle_fail_parse)
        keyword_end_equal = Optional(Suppress("end equal"))
        keyword_array = Suppress("array")
        keyword_array_index = Suppress("array index")
        keyword_if = Suppress("begin if")
        keyword_and = Suppress("and")
        keyword_or = Suppress("or")
        keyword_ns_greater_than = Keyword("greater than")
        keyword_ns_greater_than_equal = Keyword("greater than equal")
        keyword_ns_less_than = Keyword("less than")
        keyword_ns_less_than_equal = Keyword("less than equal")
        keyword_ns_not_equal = Keyword("not equal")
        keyword_ns_equal = Keyword("equal")
        keyword_then = Suppress("then")
        keyword_else = Suppress("else")
        keyword_end_if = Suppress("end if").setName("\"end if\"").setFailAction(self.handle_fail_parse)
        keyword_for = Suppress("for")
        keyword_loop = Suppress("loop")
        keyword_while = Suppress("while")
        keyword_end_for_loop = Suppress("end for").setName("\"end for loop\"").setFailAction(self.handle_fail_parse) + Optional(keyword_loop)
        keyword_end_while = Suppress("end while").setName("\"end while\"").setFailAction(self.handle_fail_parse)
        keyword_condition = Suppress("condition")
        keyword_begin = Suppress("begin")
        keyword_ns_plus_plus = Keyword("plus plus")
        keyword_ns_minus_minus = Keyword("minus minus")
        keyword_ns_plus = Keyword("plus")
        keyword_ns_minus = Keyword("minus")
        keyword_ns_times = Keyword("times")
        keyword_ns_divide = Keyword("divide")
        keyword_ns_modulo = Keyword("modulo")
        keyword_ns_plus_equal = Keyword("plus equal")
        keyword_ns_minus_equal = Keyword("minus equal")
        keyword_ns_times_equal = Keyword("times equal")
        keyword_ns_divide_equal = Keyword("divide equal")
        keyword_ns_modulo_equal = Keyword("modulo equal")
        keyword_declare = Suppress("declare")
        keyword_ns_integer = Keyword("integer")
        keyword_ns_float = Keyword("float")
        keyword_ns_double = Keyword("double")
        keyword_ns_long = Keyword("long")
        keyword_ns_void = Keyword("void")
        keyword_ns_character = Keyword("character")
        keyword_character = Suppress("character")
        keyword_string = Suppress("string")
        #keyword_end_declare = Suppress("end declare").setName("\"end declare\"").setFailAction(self.handle_fail_parse)
        keyword_end_declare = Optional(Suppress("end declare"))
        keyword_with = Suppress("with")
        keyword_size = Suppress("size")
        keyword_return = Suppress("return")
        keyword_switch = Suppress("switch")
        keyword_case = Suppress("case")
        keyword_default = Suppress("default")
        keyword_break = Suppress("break")
        keyword_continue = Suppress("continue")
        keyword_create_function = Suppress("create function")
        keyword_call_function = Suppress("call function")
        keyword_return_type = Suppress("return type")
        keyword_parameter = Suppress("parameter")
        keyword_end_function = Suppress("end function").setName("\"end function\"").setFailAction(self.handle_fail_parse)
        keyword_end_string = Suppress("end string").setName("\"end string\"").setFailAction(self.handle_fail_parse)
        keyword_end_switch = Suppress("end switch").setName("\"end switch\"").setFailAction(self.handle_fail_parse)
        space = " "
        suppress_space = Suppress(space)
        keyword_symbol = Suppress("symbol")
        symbol_ampersand = Keyword("ampersand")
        symbol_dollar = Keyword("dollar")
        symbol_percent = Keyword("percent")
        symbol_backslash = Keyword("backslash")
        symbol_colon = Keyword("colon")

        # The list of required keywords
        keywords = Keywords()
        self.list_keywords = keywords.get_keywords()

        # The components of parser
        self.literal = self.get_all_literal()
        not_all_keywords = self.build_not_all_keywords(self.list_keywords)

        symbol_expression = keyword_symbol + space + ( symbol_ampersand("amp") | symbol_dollar("dol") | symbol_percent("per") | \
                                               symbol_backslash("bac") | symbol_colon("col") )
        symbol_expression.setParseAction(self.update_symbol_expr)
         
        variable_name = Combine(OneOrMore(not_all_keywords + Word(alphas) + Optional(space)))
        character_literal = keyword_character + Word( alphas, max=1 )
        string_literal = keyword_string + Combine(OneOrMore(~keyword_end_string + \
                                                            (symbol_expression + Optional(suppress_space) | \
                                                             Word(alphas) + Optional(space)))) + keyword_end_string
        literal_name = Combine(OneOrMore(Optional(" ") + self.literal)) | character_literal("charlit") | string_literal("strlit")
        literal_name.setParseAction(self.parse_literal)
        
        variable_or_literal =  variable_name | literal_name

        # This function cannot use variable_name or it will ruin other functions due to the pre-formatting.
        variable_name_processed = Combine(OneOrMore(not_all_keywords + Word(alphas) + Optional(" ")))
        variable_name_processed.setParseAction(self.parse_var_arr_or_literal)

        for_loop = keyword_for + Optional(keyword_loop)

        comparison_operator = keyword_ns_greater_than_equal("ge") | keyword_ns_greater_than("gt") | keyword_ns_less_than_equal("le") \
                              | keyword_ns_less_than("lt") | keyword_ns_not_equal("ne") | keyword_ns_equal("eq")
        comparison_operator.setParseAction(self.update_comparison_ops) # Additional processing for output

        variable_type = keyword_ns_integer("int") | keyword_ns_float("float") | keyword_ns_double("double") | keyword_ns_long("long") | \
                        keyword_ns_void("void") | keyword_ns_character("char") # todo
        variable_type.setParseAction(self.update_var_type)

        unary_operators = (keyword_ns_plus_plus("pp") | keyword_ns_minus_minus("mm"))
        unary_operators.setParseAction(self.update_unary_operators)

        operators = keyword_ns_plus("p") |  keyword_ns_minus("min") | keyword_ns_times("t") | \
                    keyword_ns_divide("d") | keyword_ns_modulo("mod")
        operators.setParseAction(self.update_operators)

        assignment_operator = keyword_ns_equal("eq") | keyword_ns_plus_equal("pe") | keyword_ns_minus_equal("me") | \
                              keyword_ns_times_equal("te") | keyword_ns_divide_equal("de") | keyword_ns_modulo_equal("modeq")
        assignment_operator.setParseAction(self.update_assignment_operators)

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
        function_call_statement = Forward()

        mathematical_expression = Forward()
        mathematical_expression << var_arr_or_literal + ZeroOrMore(operators + mathematical_expression)
        mathematical_expression.setParseAction(self.update_join_tokens) # join completed var/arr/literal with operators

        single_expr = mathematical_expression | function_call_statement
        single_expr.setParseAction(self.update_join_tokens)
        expression = single_expr + ZeroOrMore(operators + single_expr)
        expression.setParseAction(self.parse_expression)

        parameter_without_type_stmt = Optional(keyword_with) + keyword_parameter + Optional(Combine(symbol_expression)) + expression
        parameter_without_type_stmt.setParseAction(self.update_join_tokens)

        single_conditional_expression = expression + Optional(comparison_operator + expression)
        single_conditional_expression.setParseAction(self.update_join_tokens)
        and_conditional_expression = keyword_and + single_conditional_expression
        and_conditional_expression.setParseAction(self.parse_logical_and_cond_expr)
        or_conditional_expression = keyword_or + single_conditional_expression
        or_conditional_expression.setParseAction(self.parse_logical_or_cond_expr)

        conditional_expression = single_conditional_expression + ZeroOrMore(and_conditional_expression | or_conditional_expression)
        conditional_expression.setParseAction(self.update_join_tokens)

        case_statement = keyword_case + literal_name + ZeroOrMore(statement)
        case_statement.setParseAction(self.parse_case_stmt)
        default_statement = keyword_default + ZeroOrMore(statement)
        default_statement.setParseAction(self.parse_default_stmt)

        case_or_default_stmts = case_statement | default_statement

        simple_assign_expression = variable_or_variable_with_array_index + assignment_operator + expression
        simple_assign_expression.setParseAction(self.parse_simple_assign_expression)
        postfix_expression = variable_or_variable_with_array_index + unary_operators
        postfix_expression.setParseAction(self.parse_postfix_expression)
        prefix_expression = unary_operators + variable_or_variable_with_array_index
        prefix_expression.setParseAction(self.parse_prefix_expression)

        assignment_expression = simple_assign_expression | postfix_expression | prefix_expression

        # Secondary parsable

        variable_assignment_statement = assignment_expression + keyword_end_equal
        variable_assignment_statement.setParseAction(self.parse_assignment_statement)

        if_statement = keyword_if + conditional_expression + keyword_then + ZeroOrMore(statement) + \
                           keyword_end_if
        if_statement.setParseAction(self.parse_if_statement)

        if_else_statement = keyword_if + conditional_expression + \
                            keyword_then + ZeroOrMore(statement.setResultsName("ifclause", True)) + \
                             keyword_else + ZeroOrMore(statement.setResultsName("elseclause", True)) + \
                             keyword_end_if
        if_else_statement.setParseAction(self.parse_if_else_statement)

        switch_statement = keyword_switch + expression + ZeroOrMore(case_or_default_stmts) + keyword_end_switch
        switch_statement.setParseAction(self.parse_switch_statement)

        declare_variable_statement = keyword_declare + variable_type + variable_name_processed + \
                                     Optional(keyword_equal + expression) + keyword_end_declare
        declare_variable_statement.setParseAction(self.parse_declare_var_statement)

        declare_array_statement = keyword_declare + variable_type + keyword_array + variable_with_size + \
                                  keyword_end_declare
        declare_array_statement.setParseAction(self.parse_declare_arr_statement)

        for_loop_statement = for_loop + \
                             keyword_condition + assignment_expression + \
                             keyword_condition + conditional_expression + \
                             keyword_condition + assignment_expression + keyword_begin + \
                             ZeroOrMore(statement) + keyword_end_for_loop
        for_loop_statement.setParseAction(self.parse_for_loop_statement)

        while_loop_statement = keyword_while + conditional_expression + \
                               keyword_begin + ZeroOrMore(statement) + keyword_end_while
        while_loop_statement.setParseAction(self.parse_while_loop_statement)

        return_statement = keyword_return + expression
        return_statement.setParseAction(self.parse_return_statement)

        break_statement = keyword_break
        break_statement.setParseAction(self.parse_break_statement)

        continue_statement = keyword_continue
        continue_statement.setParseAction(self.parse_continue_statement)

        function_declaration_line = keyword_create_function + variable_name + Optional(keyword_with) + keyword_return_type + \
                               variable_type + ZeroOrMore(parameter_statement.setResultsName("params", True)) + keyword_begin + \
                               ZeroOrMore(statement.setResultsName("stmts", True)) + keyword_end_function
        function_declaration_line.setParseAction(self.parse_function_declaration)

        function_call_statement << keyword_call_function + variable_name + ZeroOrMore(parameter_without_type_stmt) + \
                                keyword_end_function
        function_call_statement.setParseAction(self.parse_function_call_statement)

        # Constructs parsable
        self.assignment_statement = variable_assignment_statement

        self.selection_statement = if_statement | if_else_statement | switch_statement

        self.declaration_statement = declare_variable_statement | declare_array_statement

        self.iteration_statement = for_loop_statement | while_loop_statement

        self.jump_statement = return_statement | break_statement | continue_statement

        self.call_function_statement = function_call_statement

        statement << (self.assignment_statement | self.selection_statement | self.declaration_statement | \
                  self.iteration_statement | self.jump_statement | self.call_function_statement)

        self.function_declaration = function_declaration_line

    # This function attempts to parse repeatedly with corrections applied wherever possible.
    def parse_with_correction(self, sentence, is_initial_run = True, counter = 0, prev_exp = ""):
        result_struct = {}

        result_struct["parsed"] = ""

        if counter > 5:
            return result_struct

        result = self.parse(sentence)
        if result == "": # error message
            if is_initial_run:
                # record first expected message only
                result_struct["expected"] = self.get_error_message()
                result_struct["variables"] = self.get_variables()

            error = self.get_error_message()
            if error == "":
                result_struct["parsed"] = "" # cannot finish parsing
            else:
                error = error.replace("Expected", "")

                if error == prev_exp:
                    # reject if no improvement
                    result_struct["parsed"] = ""
                    return result_struct
                
                parts = error.split(" or ")
                new_list = []
                for part in parts:
                    new_list.append(part)

                for attempt in new_list:
                    word = attempt.replace("\"", "")

                    attempt_res = self.parse_with_correction(sentence + " " + word, False, counter + 1, error)
                    if attempt_res["parsed"] != "":
                        result_struct["parsed"] = attempt_res["parsed"]
                        result_struct["potential_missing"] = word
                        break
        else: # parsed properly
            result_struct["parsed"] = result

        return result_struct
        
 
    def parse(self, sentence, new_instance = True):
        sentence = str(sentence).lower()
        self.error_message = ""
        if new_instance:
            self.variables = []
        
        if sentence == "":
            raise Exception('Invalid statement.')

        words = sentence.split()
        if len(words) < 2:
            raise Exception('Invalid statement.')

        first_word = words[0]
        start_word = words[0] + " " + words[1]

        # Check selection statements
        if start_word == "begin if" or first_word == "switch":
            result = self.parse_check_selection_statement(sentence)
        # Check declaration statements
        elif first_word == "declare":
            result = self.parse_check_declaration_statement(sentence)
        # Check iteration statements
        elif first_word == "for" or first_word == "while":
            result = self.parse_check_iteration_statement(sentence)
        # Check jump statements (should not run as this shouldnt be at the start)
        elif first_word == "return" or first_word == "break" or first_word == "continue":
            result = self.parse_check_jump_statement(sentence)
        # Check function declaration
        elif start_word == "create function":
            result = self.parse_check_function_declaration(sentence)
        # Check call function statements
        elif start_word == "call function":
            result = self.parse_check_call_function_statement(sentence)
        # Check variable assignment statement
        elif "equal" in sentence or "plus" in sentence or "minus" in sentence:
            result = self.parse_check_variable_assignment(sentence)
        # Else, raise an exception.
        else:
            raise Exception('Invalid statement.')

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


    def parse_check_call_function_statement(self, sentence):
        return_struct = {}

        try:
            list_parsed = self.call_function_statement.parseString(sentence)
            
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

    def compare_correction(word1, word2, wp):
        result_struct = wp.parse_with_correction(word1)
        if wp.trim_all_spaces(result_struct["parsed"]) == wp.trim_all_spaces(word2):
            return "."
        else:
            print "Compare correction results wrong! "
            print word1
            print "----"
            print wp.trim_all_spaces(result_struct["parsed"])
            print "----"
            print wp.trim_all_spaces(word2)
            return "WHY YOU WRONG :("
        

    wordParser = WordParser()

    # Some quick hack unit tests
    speech = "begin if i less than two or j less than three then end if"
    struct = "if #condition #variable i < #value 2 || #variable j < #value 3 #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)
        
    speech = "switch a case zero call function hello world end function break case one a equal two end equal break " + \
                " default a equal three end equal end switch"
    struct = "switch #condition #variable a case #value 0 #case_start #function helloWorld();; break;; #case_end " + \
                " case #value 1 #case_start #assign #variable a #with #value 2;; break;; #case_end " + \
                " default #case_start #assign #variable a #with #value 3;; #case_end;; "
    print compare(speech, struct, wordParser)

    speech = "switch a case zero call function hello world end function break case one a equal two end equal break " + \
                " end switch"
    struct = "switch #condition #variable a case #value 0 #case_start #function helloWorld();; break;; #case_end " + \
                " case #value 1 #case_start #assign #variable a #with #value 2;; break;; #case_end;; "
    print compare(speech, struct, wordParser)

    speech = "switch alphabet case character a call function x end function case character b x equal one end equal end switch "
    struct = "switch #condition #variable alphabet case #value 'a' #case_start #function x();; #case_end " + \
                " case #value 'b' #case_start #assign #variable x #with #value 1;; #case_end;; "
    print compare(speech, struct, wordParser)

    speech = "switch a minus two case zero call function hello world end function break case one a equal two end equal break " + \
                " default a equal three end equal end switch"
    struct = "switch #condition #variable a - #value 2 case #value 0 #case_start #function helloWorld();; break;; #case_end " + \
                " case #value 1 #case_start #assign #variable a #with #value 2;; break;; #case_end " + \
                " default #case_start #assign #variable a #with #value 3;; #case_end;; "
    print compare(speech, struct, wordParser)
    
    speech = "max too equal numbers array index i end equal"
    struct = "#assign #variable maxToo #with #array numbers #indexes #variable i #index_end;;"
    print compare(speech, struct, wordParser)

    speech = "max equal numbers hello array index two end equal"
    struct = "#assign #variable max #with #array numbersHello #indexes #value 2 #index_end;;"
    print compare(speech, struct, wordParser)

    speech = "max equal one hundred twenty two end equal"
    struct = "#assign #variable max #with #value 122;;"
    print compare(speech, struct, wordParser)

    speech = "max equal min end equal"
    struct = "#assign #variable max #with #variable min;;"
    print compare(speech, struct, wordParser)

    speech = "max tree array index i equal min end equal"
    struct = "#assign #array maxTree #indexes #variable i #index_end #with #variable min;;"
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
    struct = "#function_declare main #function_start #function_end;;"
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

    speech = "while value less than equal three begin end while"
    struct = "while #condition #variable value <= #value 3 #while_start #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "while value less than equal three begin max equal one end equal end while"
    struct = "while #condition #variable value <= #value 3 #while_start #assign #variable max #with #value 1;; #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "while value plus two less than equal three begin end while"
    struct = "while #condition #variable value + #value 2 <= #value 3 #while_start #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "while value plus two less than equal three plus max begin end while"
    struct = "while #condition #variable value + #value 2 <= #value 3 + #variable max #while_start #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "while is done begin end while"
    struct = "while #condition #variable isDone #while_start #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "call function abc with parameter arr with parameter test end function"
    struct = "#function abc(#parameter #variable arr #parameter #variable test);;"
    print compare(speech, struct, wordParser)

    speech = "call function quick sort parameter x with parameter j plus one parameter last end function"
    struct = "#function quickSort(#parameter #variable x #parameter #variable j + #value 1 #parameter #variable last);;"
    print compare(speech, struct, wordParser)

    speech = "call function def with parameter x parameter x array index i end function"
    struct = "#function def(#parameter #variable x #parameter #array x #indexes #variable i #index_end);;"
    print compare(speech, struct, wordParser)

    speech = "max equal call function def with parameter two end function end equal"
    struct = "#assign #variable max #with #function def(#parameter #value 2);;"
    print compare(speech, struct, wordParser)
    
    speech = "begin if max less than call function def with parameter two end function then end if"
    struct = "if #condition #variable max < #function def(#parameter #value 2) #if_branch_start #if_branch_end;;"
    print compare(speech, struct, wordParser)
    
    speech = "while call function def with parameter two end function begin end while"
    struct = "while #condition #function def(#parameter #value 2) #while_start #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "call function do something end function"
    struct = "#function doSomething();;"
    print compare(speech, struct, wordParser)

    speech = "while i less than j begin call function do something end function end while"
    struct = "while #condition #variable i < #variable j #while_start #function doSomething();; #while_end;;"
    print compare(speech, struct, wordParser)

    speech = "call function print f parameter string hello end string end function"
    struct = "#function printF(#parameter #value \"hello\");;"
    print compare(speech, struct, wordParser)

    speech = "call function test parameter string hello world man end string end function"
    struct = "#function test(#parameter #value \"hello world man\");;"
    print compare(speech, struct, wordParser)

    speech = "call function abc parameter string hello end string with parameter string world end string end function"
    struct = "#function abc(#parameter #value \"hello\" #parameter #value \"world\");;"
    print compare(speech, struct, wordParser)

    speech = "declare character c equal character c end declare"
    struct = "#create char #variable c #value 'c' #dec_end;;"
    print compare(speech, struct, wordParser)

    # Test partial code
    speech = "declare integer abc "
    struct = "#create int #variable abc #dec_end;; "
    print compare_correction(speech, struct, wordParser)

    speech = "max equal two"
    struct = "#assign #variable max #with #value 2;;"
    print compare_correction(speech, struct, wordParser)

    speech = "begin if x less than y then"
    struct = "if #condition #variable x < #variable y #if_branch_start #if_branch_end;;"
    print compare_correction(speech, struct, wordParser)

    speech = "for loop condition i equal one condition i less than two condition i plus plus begin"
    struct = "for #condition #assign #variable i #with #value 1 #condition #variable i < #value 2 #condition #post #variable i ++ #for_start #for_end;;"
    print compare_correction(speech, struct, wordParser)

    speech = "begin if x less than y then max equal two"
    struct = "if #condition #variable x < #variable y #if_branch_start #assign #variable max #with #value 2;; #if_branch_end;;"
    print compare_correction(speech, struct, wordParser)

