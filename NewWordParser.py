#!/usr/bin/env python2

import re
from word2number import w2n # External library to parse words to numbers
from pyparsing import * # External parser library
from Keywords import Keywords

class WordParser:
    SPECIAL_SPACE_CHAR = "^sp"
    
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
            return " #value {}".format(str(w2n.word_to_num(word)))
        elif "\"" in word: # if is string
            if word[len(word) - 2] == " ": # if space at last character before "
                processed_str = " #value {}\"".format(word[:-2]) # remove the space
            else:
                processed_str = " #value {}".format(word)
            return processed_str.replace(WordParser.SPECIAL_SPACE_CHAR, " ")
        elif "'" in word: # if is character
            return " #value {}".format(word)
        else:
            try:
                # if word is already in number form
                float(word)

                return " #value {}".format(str(word))
            except ValueError:
                if special_syntax_if_var == None:
                    return " #variable {}".format(self.build_var_name(word))
                else:
                    return " {} {}".format(special_syntax_if_var, self.build_var_name(word))
                

    def parse_var_arr_or_literal(self, toks):
        word = toks[0]

        try:
            # Test if word is an array
            tokens = self.array_index_phrase.parseString(word)

            # array
            return "#array  {} #indexes {} #index_end".format(self.build_var_name(tokens[0]), \
                                                              self.process_variable_or_literal(tokens[1]))
        except ParseException: # no match: not an array
            return self.process_variable_or_literal(word)


    def parse_var_arr_or_literal_word(self, word):
        return self.parse_var_arr_or_literal([word])
    

    def parse_arr_with_size(self, toks):
        var_name = self.build_var_name(toks[0])
        size = toks[1]

        return "#variable {} #indexes {} #index_end".format(var_name, self.process_variable_or_literal(size))


    ## This is for setting parse action to output array tags
    def update_array_tags(self, tokens):
        return " #array {} #index {}".format(tokens.varname, tokens.index)


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

            return " #parameter_a #dimension 1 {} #array {}".format(var_type, variable_name)
        except ParseException: # no match: not an array, but a variable
            variable_name = self.build_var_name(var_or_array)

            # Add to variables list.
            self.add_variable_by_word(variable_name)
            
            return " #parameter {}{}".format(var_type, variable_name)


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
        elif tokens.equ != "": # equal
            return "="
        elif tokens.dot != "": # dot
            return "."
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
            return "'{}'".format(tokens[0])
        elif tokens.strlit != "": # string literal
            return "\"{}\"".format(tokens[0])
        else: # normal literal (number / floating pt number)
            return tokens
        

    def update_join_tokens(self, tokens):
        return ' '.join(tokens)


    def parse_simple_assign_expression(self, tokens):
        # tokens consist of [ var_or_arr, assignment_operator, expression ]
        return "#assign {} {} {}".format(self.parse_var_arr_or_literal_word(tokens[0]), tokens[1], tokens[2])


    def parse_postfix_expression(self, tokens):
        # tokens consist of [ var_or_arr, unary_operator ]
        return "#post {} {}".format(self.parse_var_arr_or_literal_word(tokens[0]), tokens[1])


    def parse_prefix_expression(self, tokens):
        # tokens consist of [ unary_operator, var_or_arr ]
        return "{} {}".format(tokens[0], self.parse_var_arr_or_literal_word(tokens[1]))


    def parse_assignment_statement(self, tokens):
        # tokens consist of [ assignment_expression ]
        parsed_stmt = "{};; ".format(tokens[0])
        
        return parsed_stmt


    def parse_if_statement(self, tokens):
        # tokens consist of [ conditional_expression, statements (multiple) ]
        parsed_stmt = "if #condition {} #if_branch_start ".format(tokens[0])

        cond_stmt = [tokens[i] for i in range(1, len(tokens))]
        mid_stmt = " ".join(cond_stmt)

        return "{} {} #if_branch_end;;".format(parsed_stmt, mid_stmt)


    def parse_if_else_statement(self, tokens):
        # tokens consist of [ conditional_expression, statements (multiple) ]
        # statements are split into ifclause statements and elseclause statements
        first_stmt = "if #condition {} #if_branch_start ".format(tokens[0])
        else_list = []

        if_list = [tokens.ifclause[i] for i in range(0, len(tokens.ifclause))]

        mid_stmt = " #if_branch_end #else_branch_start "

        else_list = [tokens.elseclause[j] for j in range(0, len(tokens.elseclause))]

        if_stmt = " ".join(if_list)
        else_stmt = " ".join(else_list)
            
        return "{} {} {} {} #else_branch_end;;".format(first_stmt, if_stmt, mid_stmt, else_stmt)


    def parse_for_loop_statement(self, tokens):
        # tokens consist of [ assignment_expression, conditional_expression, assignment_expression,
        # statements (multiple)]
        parsed_stmt = "for #condition {} #condition {} #condition {} #for_start ".format( \
            tokens[0], tokens[1], tokens[2])

        body_list = [tokens[i] for i in range(3, len(tokens))]

        return "{} {} #for_end;;".format(parsed_stmt, " ".join(body_list))


    def parse_while_loop_statement(self, tokens):
        # tokens consist of [ conditional_expression, statements (multiple) ]
        parsed_stmt = "while #condition {} #while_start ".format(tokens[0])

        body_list = [tokens[i] for i in range(1, len(tokens))]

        return "{} {} #while_end;;".format(parsed_stmt, " ".join(body_list))


    def parse_function_declaration(self, tokens):
        # tokens consist of [ var_name, var_type, parameter_statements (multiple) + statement (multiple) ]
        # statements are tokens.stmts and parameter_statements are token.params
        function_name = self.build_var_name(tokens[0])

        # add function name to variables list.
        self.add_variable_by_word(function_name)

        param_list = [tokens.params[i] for i in range(0, len(tokens.params))]
        param_stmt = "".join(param_list)

        body_list = [tokens.stmts[j] for j in range(0, len(tokens.stmts))]
        body_stmt = " ".join(body_list)

        parsed_stmt = "#function_declare {} {} {} #function_start {} #function_end;;".format( \
            function_name, tokens[1], param_stmt, body_stmt)

        return parsed_stmt


    def parse_function_call_statement(self, tokens):
        # tokens consist of [ var_name, parameter_statements (multiple)]
        param_list = []
        for i in range(1, len(tokens)):
            param_list.append("#parameter")
            param_list.append(tokens[i])
        param_stmt = " ".join(param_list)
        
        return "#function {}({});;".format(self.build_var_name(tokens[0]), param_stmt)
        

    def parse_case_stmt(self, tokens):
        # tokens consist of [ literal_name, statements (multiple)]
        stmt_list = [tokens[i] for i in range(1, len(tokens))]
        stmt = " ".join(stmt_list)

        return " case {} #case_start {} #case_end".format(self.process_variable_or_literal(tokens[0]), stmt)

    def parse_default_stmt(self, tokens):
        # tokens consist of [ statements (multiple)]
        stmt_list = [tokens[i] for i in range(0, len(tokens))]
        stmt = " ".join(stmt_list)

        return " default #case_start {} #case_end".format(stmt)


    def parse_switch_statement(self, tokens):
        # tokens consist of [ conditional_expression, case/default stmts (multiple) ]
        stmt_list = [tokens[i] for i in range(1, len(tokens))]
        stmt = " ".join(stmt_list)

        return " switch #condition {} {};;".format(tokens[0], stmt)


    def parse_logical_and_cond_expr(self, tokens):
        # tokens consist of [ conditional_expression ]
        parsed_stmt = " && {}".format(tokens[0])
        return parsed_stmt


    def parse_logical_or_cond_expr(self, tokens):
        # tokens consist of [ conditional_expression ]
        parsed_stmt = " || {}".format(tokens[0])
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
        if len(tokens) == 3:
            parsed_stmt = "#create {} {} {} #dec_end;;".format(tokens[0], tokens[1], tokens[2])
        else:
            parsed_stmt = "#create {} {} #dec_end;;".format(tokens[0], tokens[1])

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
        
        return "#create {} #array {} #dec_end;;".format(tokens[0], tokens[1])

    def parse_return_statement(self, tokens):
        # tokens consist of [ expression ]
        return "return {};;".format(tokens[0])

    def parse_space(self, tokens):
        return WordParser.SPECIAL_SPACE_CHAR

    def parse_break_statement(self, tokens):
        # no tokens here.
        return "break;;"

    def parse_continue_statement(self, tokens):
        # no tokens here.
        return "continue;;"

    def parse_rest_of_line(self, tokens):
        self.rest_of_line = tokens[1]
        return tokens[0]

    def handle_fail_parse(self, string, loc, expr, err):
        if self.error_message != "":
            self.error_message += " or {}".format(str(expr))
        else:
            self.error_message = str(expr)

    def get_error_message(self):
        parts = self.error_message.split(" or ")
        parts = [part.strip() for part in parts]
        
        parts_without_duplicate = {part for part in parts} # set comprehension
        parts_without_duplicate = list(parts_without_duplicate)

        error_message = " or ".join(parts_without_duplicate)
        
        return "Expected {}".format(error_message)


    def get_variables(self):
        var_list = {variable for variable in self.variables} #set
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
        keyword_space = Keyword("space")
        keyword_space.setParseAction(self.parse_space)
        keyword_symbol = Suppress("symbol")
        symbol_ampersand = Keyword("ampersand")
        symbol_dollar = Keyword("dollar")
        symbol_percent = Keyword("percent")
        symbol_backslash = Keyword("backslash")
        symbol_colon = Keyword("colon")
        symbol_dot = Keyword("dot")
        symbol_equal = Keyword("equal")

        # The list of required keywords
        keywords = Keywords()
        self.list_keywords = keywords.get_keywords()

        # The components of parser
        self.literal = self.get_all_literal()
        not_all_keywords = self.build_not_all_keywords(self.list_keywords)

        symbol_expression = keyword_symbol + space + ( symbol_ampersand("amp") | symbol_dollar("dol") | symbol_percent("per") | \
                                               symbol_backslash("bac") | symbol_colon("col") | symbol_dot("dot") | \
                                                symbol_equal("equ") )
        symbol_expression.setParseAction(self.update_symbol_expr)
         
        variable_name = Combine(OneOrMore(not_all_keywords + Word(alphas) + Optional(space)))
        character_literal = keyword_character + Word( alphas, max=1 )
        string_literal = keyword_string + Combine(OneOrMore(~keyword_end_string + \
                                                            ( keyword_space + Optional(suppress_space) | \
                                                             symbol_expression + ZeroOrMore(suppress_space) | \
                                                             Word(alphanums) + Optional(space)))) + keyword_end_string
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
                             keyword_condition + assignment_expression + keyword_end_equal + \
                             keyword_condition + conditional_expression + \
                             keyword_condition + assignment_expression + keyword_end_equal + \
                             keyword_begin + ZeroOrMore(statement) + keyword_end_for_loop # all end equal must be optional, suppress

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

        # Constructs parsable (temp_ prefixed is required so as to parse nested statements)
        self.assignment_statement = variable_assignment_statement + restOfLine
        temp_assignment_statement = variable_assignment_statement
        self.assignment_statement.setParseAction(self.parse_rest_of_line)

        self.selection_statement = (if_statement | if_else_statement | switch_statement) + restOfLine
        temp_selection_statement = if_statement | if_else_statement | switch_statement
        self.selection_statement.setParseAction(self.parse_rest_of_line)

        self.declaration_statement = (declare_variable_statement | declare_array_statement) + restOfLine
        temp_declaration_statement = declare_variable_statement | declare_array_statement
        self.declaration_statement.setParseAction(self.parse_rest_of_line)

        self.iteration_statement = (for_loop_statement | while_loop_statement) + restOfLine
        temp_iteration_statement = for_loop_statement | while_loop_statement
        self.iteration_statement.setParseAction(self.parse_rest_of_line)

        self.jump_statement = (return_statement | break_statement | continue_statement) + restOfLine
        temp_jump_statement = return_statement | break_statement | continue_statement
        self.jump_statement.setParseAction(self.parse_rest_of_line)

        self.call_function_statement = function_call_statement + restOfLine
        temp_call_function_statement = function_call_statement
        self.call_function_statement.setParseAction(self.parse_rest_of_line)

        statement << (temp_assignment_statement | temp_selection_statement | temp_declaration_statement | \
                  temp_iteration_statement | temp_jump_statement | temp_call_function_statement)

        self.function_declaration = function_declaration_line + restOfLine
        self.function_declaration.setParseAction(self.parse_rest_of_line)

    # This function attempts to parse repeatedly with corrections applied wherever possible.
    def parse_with_correction(self, sentence, is_initial_run = True, counter = 0):
        result_struct = {}

        result_struct["parsed"] = ""

        if counter > 5:
            return result_struct

        try:
            temp_res = self.match_construct(sentence)
            if temp_res["has_match"]:
                result = temp_res["struct_cmd"]
            else:
                result = ""
        except:
            if is_initial_run:
                result_struct["expected"] = self.get_error_message()
                result_struct["variables"] = self.get_variables()
            result_struct["parsed"] = ""

            return result_struct
            
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
                
                parts = error.split(" or ")
                new_list = [part for part in parts]

                for attempt in new_list:
                    word = attempt.replace("\"", "")

                    attempt_res = self.parse_with_correction(sentence + " " + word, False, counter + 1)
                    if attempt_res["parsed"] != "":
                        result_struct["parsed"] = attempt_res["parsed"]
                        result_struct["potential_missing"] = word
                        break
        else: # parsed properly
            result_struct["parsed"] = result

        return result_struct


    def match_construct(self, sentence):
        if sentence == "":
            raise Exception('Invalid statement.')

        words = sentence.split()
        first_word = ""
        start_word = ""
        
        if len(words) < 2:
            first_word = words[0]
            start_word = words[0]
        else:
            first_word = words[0]
            start_word = "{} {}".format(words[0], words[1])
            
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

        return result

    def need_to_append_end_equal(self, sentence):
        if sentence == "":
            return False

        if "begin" in sentence or "then" in sentence or "condition" in sentence or "while" in sentence or "for" in sentence \
           or "string" in sentence:
            return False

        if "equal" in sentence or "plus" in sentence or "minus" in sentence:
            result = self.parse_check_variable_assignment(sentence)
            if result["has_match"]:
                try:
                    if sentence.split()[-2:] == "end equal":
                        return False
                    else:
                        return True
                except:
                    return False
        
        return False
        
 
    def parse(self, sentence, new_instance = True, result_struct = {}):
        # Result_structure returned contains the following:
        # sentence_status  : True / False depending on whether sentence can be parsed or not. Array.
        # variables        : var_list . Array
        # parsed           : struct command (completed) . Array
        # text             : raw text (only those parse-able) without correction. Array
        # expected         : expected "end declare" for example. Single element
        # potential_missing: one missing construct like "end for loop" for example. Single element.

        sentence = str(sentence).lower().strip()
        self.error_message = ""
        self.rest_of_line = ""
        self.variables = []

        result = self.match_construct(sentence)

        if new_instance:
            result_struct["sentence_status"] = [] # True / False depending on whether sentence can be parsed or not.
            result_struct["variables"] = [] # var_list
            result_struct["parsed"] = [] # struct command (completed)
            result_struct["text"] = [] # raw text (only those parse-able) without correction
            result_struct["expected"] = "" # expected "end declare" for example.
            result_struct["potential_missing"] = "" # one missing construct like "end for loop" for example.
            result_struct["func_dec_complete"] = [] # tell if function declaration statement is complete, or partial.

        if result["has_match"]:
            result_struct["sentence_status"].append(True)
            result_struct["variables"].append(self.get_variables())
            result_struct["parsed"].append(self.trim_all_spaces(result["struct_cmd"]))

            parsed_text, rest_text = self.split_parsed_and_rest(sentence, self.rest_of_line)
            result_struct["text"].append(parsed_text)
            if "func_dec_complete" in result.keys():
                result_struct["func_dec_complete"].append(result["func_dec_complete"])
            else:
                result_struct["func_dec_complete"].append(True)
            
            if str(rest_text).strip() != "":
                result_struct = self.parse(rest_text, new_instance = False, result_struct = result_struct)
            
            return result_struct
        else:
            # no matches
            temp_result = self.parse_with_correction(sentence)

            result_struct["sentence_status"].append(False)
            result_struct["variables"].append(temp_result["variables"])
            result_struct["parsed"].append(temp_result["parsed"])
            result_struct["text"].append(sentence)
            result_struct["expected"] = temp_result["expected"]
            if "func_dec_complete" in result.keys():
                result_struct["func_dec_complete"].append(result["func_dec_complete"])
            else:
                result_struct["func_dec_complete"].append(True)

            if "potential_missing" in temp_result.keys():
                result_struct["potential_missing"] = temp_result["potential_missing"]
            else:
                result_struct["potential_missing"] = ""

            return result_struct

    def split_parsed_and_rest(self, input_sentence, rest_of_line):
        if rest_of_line.strip() == "":
            return self.trim_all_spaces(input_sentence.strip()), ""
            
        start_index = input_sentence.index(rest_of_line)
        parsed_part = input_sentence[0:start_index]
        processed_parsed_part = self.trim_all_spaces(parsed_part.strip())
        processed_rest_part = self.trim_all_spaces(rest_of_line.strip())
        
        return processed_parsed_part, processed_rest_part
        

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
            return_struct["func_dec_complete"] = True 
        except ParseException:
            return_struct["has_match"] = False
            if "begin" in sentence:
                return_struct["func_dec_complete"] = True
            else:
                return_struct["func_dec_complete"] = False

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
    wordParser = WordParser()

    while True:
        input_word = raw_input("Type speech : ")
        try:
            res_struct = wordParser.parse(input_word)

            print "Text object : " + str(res_struct["text"])
            print "Variables : " + str(res_struct["variables"])
            print "Sentence status : " + str(res_struct["sentence_status"])
            print "Expected : " + str(res_struct["expected"]) + " || Potential missing : " + str(res_struct["potential_missing"])
            print "Struct Cmd : " + str(res_struct["parsed"])
        except Exception as e:
            print "Exception encountered : "
            print str(e)
    
