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

        
        
    def __init__(self):
        # Define all keywords here
        keyword_equal = Suppress("equal")
        keyword_end_equal = Suppress("end equal")
        keyword_array_index = Suppress("array index")

        # The list of required keywords
        list_keywords = ["equal", "end equal", "array index"]

        # The components of parser
        not_all_keywords = self.build_not_all_keywords(list_keywords)
        self.literal = self.get_all_literal()
        
        variable_name = Combine(ZeroOrMore(not_all_keywords + Word(alphas) + " "))
        literal_name = OneOrMore(self.literal)
        variable_or_literal = variable_name | literal_name

        variable_with_array_index = variable_name("varname") + keyword_array_index + variable_or_literal("index")
        # Additional processing for output
        variable_with_array_index.setParseAction(self.update_array_tags)

        self.array_index_phrase = Suppress("#array") + variable_name + Suppress("#index") + variable_or_literal

        variable_or_variable_with_array_index = variable_with_array_index | variable_name

        var_optional_array_index_or_literal = variable_or_variable_with_array_index | literal_name

        # Constructs parsable
        self.assign_var_stmt = var_optional_array_index_or_literal + keyword_equal + var_optional_array_index_or_literal + keyword_end_equal
        

    def parse(self, sentence):
        # Run parsing through each construct

        # Check variable assignment
        result = self.parse_check_variable_assignment(sentence)
        if result["has_match"]:
            return self.trim_all_spaces(result["struct_cmd"])
        
        

    def parse_check_variable_assignment(self, sentence):
        return_struct = {}

        try:
            list_match_tokens = self.assign_var_stmt.parseString(sentence)

            return_struct["has_match"] = True
            return_struct["struct_cmd"] = "#assign " + self.process_var_or_arr_or_literal(list_match_tokens[0]) + " #with " + \
                    self.process_var_or_arr_or_literal(list_match_tokens[1]) + ";;"
            
        except ParseException:
            return_struct["has_match"] = False

        return return_struct
            


if __name__ == "__main__":
    wordParser = WordParser()

    # Some quick hack unit tests
    print wordParser.parse("max two equal numbers array index i end equal") == \
          "#assign #variable maxTwo #with #array numbers #indexes #variable i #index_end;;"
    print wordParser.parse("max equal numbers hello array index two end equal") == \
          "#assign #variable max #with #array numbersHello #indexes #value 2 #index_end;;"
    print wordParser.parse("max equal one hundred and twenty two end equal") == \
          "#assign #variable max #with #value 122;;"
    print wordParser.parse("max equal min end equal") == "#assign #variable max #with #variable min;;"
    print wordParser.parse("max three array index i equal min end equal") == \
          "#assign #array maxThree #indexes #variable i #index_end #with #variable min;;"
    print wordParser.parse("max array index twenty one equal min end equal") == \
          "#assign #array max #indexes #value 21 #index_end #with #variable min;;"



