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
        
        
    def __init__(self):
        # Define all keywords here
        keyword_equal = Suppress("equal")
        keyword_end_equal = Suppress("end equal")

        # The list of required keywords
        list_keywords = ["equal", "end equal"]

        # The components of parser
        not_all_keywords = self.build_not_all_keywords(list_keywords)
        literal = self.get_all_literal()
        
        variable_name = Combine(ZeroOrMore(not_all_keywords + Word(alphas) + " "))
        literal_name = OneOrMore(literal)
        variable_or_literal = variable_name | literal_name       
        
        assign_var_stmt = variable_name + keyword_equal + variable_or_literal + keyword_end_equal
        
        for assign_stmt in assign_var_stmt.scanString("max equal numbers array index i end equal"):
            result = assign_stmt[0]
            print "#assign " + result[0] + " #with " + result[1] + " #index_end;;"

        print "next case\n"
        for assign_stmt in assign_var_stmt.scanString("max equal one hundred and twenty two end equal"):
            result = assign_stmt[0]
            print "#assign " + result[0] + " #with " + result[1] + " #index_end;;"
        
    #max equal numbers array index i end equal
    #=>
    #assign #variable max #with #array  numbers #indexes  #variable  i #index_end;;

wordParser = WordParser()

