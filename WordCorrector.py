#!/usr/bin/env python2
import re
from num2words import num2words
from word2number import w2n
import hashlib
from Keywords import Keywords, Keyword as KeywordObj
from StandardFunctions import StandardFunctions
from WordSimilarity import get_most_similar_word, sounds_like_index, get_num_syllable

class WordCorrector:
    def __init__(self, words, var_list, create_func_complete=True, open_string=False):
        self.corrected = ""
        self.space = ""
        self.var_types = ["integer", "long", "float", "double", "boolean", "character", "string", "void"]
        self.variables_list = var_list
        self.std_functions = StandardFunctions().get_std_functions()
        self.kw = Keywords()
        self.max_syllable = self.kw.get_max_num_syllable()
        self.keyword_list = self.kw.get_keywords()
        self.word_syllable_list = self.build_word_syllable_list(self.kw)
        self.correction_list = self.word_syllable_list
        self.regex_alpha_or_numeric = re.compile(r'([A-Za-z]+)(-?((\d+\.\d+)|\d+))') # match alphabet then number
        self.regex_symbol_dot = re.compile(r'symbol\s?\.') # match symbol . or symbol.

        words_without_math_operators = self.replace_symbols(words)
        words_with_corrected_symbol_word = self.correct_symbol_words( \
                                    words_without_math_operators, self.max_syllable).strip()
        word_list = words_with_corrected_symbol_word.split(" ")
        self.words_list = self.separate_numbers_from_words(word_list)
        if create_func_complete is None:
            self.create_func_complete = True
        else:
            self.create_func_complete = create_func_complete
        self.open_string = open_string

    def replace_symbols(self, words):
        words_without_plus = words.replace("+", " plus ")
        words_without_minus = words_without_plus.replace("-", " minus ")
        words_without_times = words_without_minus.replace(" x ", " times ")
        words_without_divide = words_without_times.replace("/", " divide ")
        words_without_dot = re.sub(self.regex_symbol_dot, "symbol dot ", words_without_divide)
        final_words = words_without_dot.replace(" X ", " times ")
        final_words = final_words.replace(" * ", " times ")

        return final_words

    def separate_numbers_from_words(self, word_list):
        temp_list = []
        for word in word_list:
            regex_match = re.match(self.regex_alpha_or_numeric, word)
            if regex_match is not None:
                alpha_part = regex_match.group(1)
                num_part = regex_match.group(2)
                temp_list.append(alpha_part)
                temp_list.append(num_part)
            else: # no match
                temp_list.append(word)

        return temp_list

    def run_correction(self):
        return self.run_correct_words_multiple("")

    def run_correct_words_multiple(self, prev_hash = ""):
        self.correct_words()

        hashed_item = self.hash_string(self.corrected)

        if hashed_item != prev_hash:
            self.reinit()
            return self.run_correct_words_multiple(hashed_item)
        else:
            return self.corrected

    def hash_string(self, string):
        return hashlib.md5(str(string)).hexdigest()

    def reinit(self):
        self.words_list = self.corrected.split(" ")
        self.corrected = ""
        self.space = ""

    def get_word(self, index):
        if len(self.words_list) > index:
            return self.words_list[index].lower()
        else:
            return ""

    def correct_symbol_words(self, words, max_syllable, corrected=""):
        if "symbol" not in words:
            return "{} {}".format(corrected, words)

        index = words.index("symbol")
        if corrected == "":
            corrected = "{}symbol ".format(words[:index])
        else:
            corrected = "{} {}symbol ".format(corrected, words[:index])

        try:
            words = words[index + 7:]
        except:
            return corrected

        parts = words.strip().split(" ")
        if len(parts) == 0 or (len(parts) == 1 and parts[0] == ""):
            return corrected

        # part_word[0] consist of one word, part_word[1] consist of 2 words etc.
        part_word = [" ".join(parts[0:i+1]) for i in range(0, min(max_syllable, len(parts)))]

        # Match wrong word with the correct keyword.
        max_sim = -1
        temp_wrong_word_index = -1
        temp_correct_word = ""
        
        is_same_word = False
        
        for keyword_pair in self.correction_list:
            keyword = keyword_pair.get_keyword()
            syllable = keyword_pair.get_syllable()
            # some keywords are not so common, or not so easily mispronounced,
            # they need a min sim index to allow the correction.
            # Normally, this value is 0 to signify this is not a special case.
            keyword_min_correction_value = keyword_pair.get_min_correct()
            num_part_query = min(syllable, len(parts))

            if ((int(keyword_pair.get_symbol_bits()) & 1) == 0): # get LSB from 2-bit item. Can be symbol-word
                continue

            # A word with j syllable can be matched with 1 to j wrong words.
            # Higher j is prioritised, thus the use of reversed here.
            for j in list(reversed(range(0, num_part_query))):
                curr_wrong_word = part_word[j].lower()

                if curr_wrong_word == keyword:
                    is_same_word = True
                    break

                # Common error which is not corrected by algorithm.
                if (curr_wrong_word == "and percent" or curr_wrong_word == "and person" or curr_wrong_word == "in person")\
                   and keyword == "ampersand":
                    curr_sim = 1.0
                else:
                    curr_sim = sounds_like_index(curr_wrong_word, keyword, must_match=True)

                if curr_sim > max_sim and curr_sim > keyword_min_correction_value:
                    # Example: Don't correct "length with parameter integer" --> "parameter" 
                    if not self.is_part_of(curr_wrong_word, keyword):
                        max_sim = curr_sim
                        temp_wrong_word_index = j
                        temp_correct_word = keyword

            if is_same_word:
                break

        if max_sim > -1 and not is_same_word: # if there is a high similarity word.
            corrected += temp_correct_word
            remaining_wrong_words = parts[temp_wrong_word_index+1: len(parts)]
            return self.correct_symbol_words(" ".join(remaining_wrong_words), max_syllable, corrected)
        else: # cannot find any match or is the same word (no need correction)
            corrected += part_word[0]
            remaining_wrong_words = parts[1: len(parts)]
            return self.correct_symbol_words(" ".join(remaining_wrong_words), max_syllable, corrected)  

    def premature_correction(self):
        list_end_constructs = ["if", "declare", "equal", "function", "for", "fall", "switch", "while", "string"]
        
        for i in range(0, len(self.words_list)):
            # correct and -> end for end constructs.
            # Reason: For example, "and declare" makes more sense as an English phrase as compared to "end declare".
            # "And" is normally used as a function word to indicate the connection of items, whereas "End declare"
            # is normally used as a programming construct and not as English phrase. This correction also could not
            # be done by part 2 of the module as "and" itself is a keyword, which is an acceptable word.
            # Classification: Specific to English Language
            if (self.get_word(i) == "and" or (self.get_word(i) == "n") and "n" not in self.variables_list) \
               and self.get_word(i+1) in list_end_constructs:
                self.words_list[i] = "end"
            # correct standard functions print f and scan f
            # Reason:  "printf" and "scanf" are function names and they make no sense in English.
            # For English, "print f" is a more proper phrase which means to produce the letter "f" in a mechanical process
            # called printing.
            # Classification: Specific to English Language
            elif (self.get_word(i) == "print" or self.get_word(i) == "scan") and self.get_word(i+1) == "f":
                self.words_list[i] += "f"
                self.words_list[i+1] = ""
            # correct equal to -> equal two if "to" is not a variable
            # Reason: "equal to" is a proper English phrase as opposed to "equal two" which sounds like improper
            # English with a missing preposition "to". ("equal to two") 
            # Classification: Specific to English Language
            elif self.get_word(i) == "equal" and self.get_word(i+1) == "to" and "to" not in self.variables_list:
                if self.get_word(i+2) == "" or self.get_word(i+2) == "end":
                    self.words_list[i+1] = "two"
                else:
                    self.words_list[i+1] = ""    
            # correct ii if needed
            # Reason: Sometimes, Google Cloud Speech will be too smart and read `second` as `II` which is the Roman
            # numeral for 2.
            # Classification: Specific to Google Cloud Engine
            elif self.get_word(i) == "ii":
                if "i" in self.variables_list:
                    self.words_list[i] = "i"
                elif "second" in self.variables_list:
                    self.words_list[i] = "second"
            # correct common error: condition is --> condition i
            # Reason: "condition i" is more of a programming construct, whereas "condition is" is a proper English phrase.
            # Moreover, "i" tends to be a pronoun and is not used as a pronoun in this instance, thus it tends
            # to get misread as "condition is" instead.
            # Classification: Specific to English Language
            elif self.get_word(i) == "condition" and self.get_word(i+1) == "is":
                if "i" in self.variables_list and "is" not in self.variables_list:
                    self.words_list[i+1] = "i"
            # correct missing iterators
            # Reason: Google Cloud Speech can sometimes mistake single alphabet iterators as noise and totally omit them from
            # recognition.
            # Classification: Specific to Google Cloud Engine
            elif self.get_word(i) == "condition" and self.get_word(i+1) in ["equal", "greater", "less"]:
                if "i" in self.variables_list:
                    self.words_list[i+1] = "i " + self.words_list[i+1]
                elif "j" in self.variables_list:
                    self.words_list[i+1] = "j " + self.words_list[i+1]
            # correct begin eve, begin is --> begin if
            # Reason: All these words make no sense in English (Examples: begin eve, end eve), but they ("eve", "if", "is")
            # can sound quite similar. Thus, we need to correct them into our proper structured language constructs. 
            # Classification: Specific to English Language
            elif (self.get_word(i) == "begin" or self.get_word(i) == "end") and \
                 (self.get_word(i+1) == "eve" or self.get_word(i+1) == "is" or self.get_word(i+1) == "east" or self.get_word(i+1) == "this"):
                if self.words_list[i+1] not in self.variables_list:
                    self.words_list[i+1] = "if"
            # correct reef --> with
            # Reason: "with" and "reef" sound similar and it is often misrecognised as "reef" by Google Cloud Engine
            # Classification: can be both English Language or Google Cloud Engine
            elif self.get_word(i) == "reef":
                if "reef" not in self.variables_list:
                    self.words_list[i] = "with"
            # correct divide by --> divide
            # Reason: Google Cloud will try to be smart and mistakenly thought that there is a missing "by" after the
            # word "divide" as it is quite common to say "divide by" in English as a math operator. 
            # Classification: Specific to Google Cloud Engine
            elif self.get_word(i) == "divide" and self.get_word(i+1) == "by":
                if "by" not in self.variables_list:
                    self.words_list[i+1] = ""
            # correct NY Lo --> end while
            # Reason: Google Cloud will sometimes misinterpret "end while" as "NY Lo".
            # This could be due to how the recognition engine is being trained with American datasets.
            # In the American context, "NY Lo" can refer to the NYLO Hotels or the New York Lottery.
            # Classification: Specific to Google Cloud Engine
            elif self.get_word(i) == "ny" and self.get_word(i+1) == "lo":
                self.words_list[i] = "end"
                self.words_list[i+1] = "while"

    def get_create_func_correction_list(self):
        required_list = self.var_types + ["function", "with", "return", "type", "parameter", "begin"]
        create_func_correction_list = self.build_custom_word_syllable_list(required_list)
        
        self.correction_list = create_func_correction_list
        

    def correct_words(self):
        temp_words = []
        word_to_add = ""
        self.is_correction_done = False
        to_correct_prev_wrong_words = False

        self.premature_correction()

        # handle special cases first.
        if not self.create_func_complete:
            self.get_create_func_correction_list()
        elif self.has_next_word():
            if self.query_next_word() == "declare":
                # declaring variables does not trigger normal correction
                self.get_next_word()
                self.add_word_to_corrected("declare")
                
                required_list = self.var_types + ["declare", "equal", "index"]
                declare_correction_list = self.build_custom_word_syllable_list(required_list)
                
                self.correction_list = declare_correction_list
            elif len(self.words_list) >= 2 and self.words_list[0] == "create" and self.words_list[1] == "function":
                # create function does not trigger normal correction
                self.get_next_word()
                self.get_next_word()
                self.add_word_to_corrected("create function")
                
                self.get_create_func_correction_list()
        
        # perform the correction        
        while (self.has_next_word()):
            is_string_encountered = False
            is_char_encountered = False
            current_word = self.get_next_word()

            if self.open_string:
                if current_word == "end" and self.query_next_word() == "string":
                    self.get_next_word() # get the string word.
                    words_yet_to_add = " ".join(self.words_list)
                    self.open_string = False

                    self.add_word_to_corrected("end string")
                    self.words_list = words_yet_to_add.split(" ")
                else:
                    self.reinsert_word(current_word)
                    is_string_encountered = True
                    to_correct_prev_wrong_words = False
                    word_to_add = ""
            elif (self.is_number(current_word)):
                # Convert numbers to words (e.g. 42 -> forty-two)
                number_in_word_form = num2words(float(current_word))
                word_to_add = number_in_word_form
                to_correct_prev_wrong_words = True
            elif (current_word == "string"):
                # do not correct strings
                word_to_add = current_word
                to_correct_prev_wrong_words = True
                is_string_encountered = True
            elif (current_word == "character"):
                # do not correct characters
                word_to_add = current_word
                to_correct_prev_wrong_words = True
                is_char_encountered = True
            elif (current_word == "if"):
                # special case: "if" does not follow from a "begin"
                prev_word = self.query_latest_added_word()
                if prev_word != "begin" and prev_word != "end":
                    temp_words.append("eve") # because `if` is a keyword
                    to_correct_prev_wrong_words = False
                else:
                    word_to_add = current_word
                    to_correct_prev_wrong_words = True
            elif (current_word in self.variables_list or current_word in self.keyword_list or current_word in w2n.american_number_system):
                # do not correct any variables or keywords (including numbers)

                # Handle special cases:
                prev_word = self.query_latest_added_word()
                if current_word == "than" and prev_word != "greater" and prev_word != "less":
                    current_word = "then"
                elif current_word == "then" and (prev_word == "greater" or prev_word == "less"):
                    current_word = "than"                    
                word_to_add = current_word
                to_correct_prev_wrong_words = True
            else:
                # wrong words to perform correction
                temp_words.append(current_word)
                to_correct_prev_wrong_words = False
                
            if to_correct_prev_wrong_words:
                self.is_correction_done = self.perform_correction(" ".join(temp_words), self.correction_list, self.max_syllable)
                self.add_word_to_corrected(word_to_add)
                word_to_add = ""
                temp_words = []

            if is_string_encountered:
                is_string_encountered = False

                words_yet_to_add = " ".join(self.words_list)
                index_end_string = -1
                try:
                    index_end_string = words_yet_to_add.index("end string")
                except ValueError:
                    pass
                
                if index_end_string == -1: # no end string found.
                    self.add_word_to_corrected(words_yet_to_add)
                    break
                else: # end string found
                    self.add_word_to_corrected(words_yet_to_add[0: index_end_string + 10])
                    self.words_list = words_yet_to_add[index_end_string + 10:].strip().split(" ")
            elif is_char_encountered:
                is_char_encountered = False
                next_word = self.get_next_word()
                self.add_word_to_corrected(next_word)

            if self.is_correction_done:
                # Restart the correction progress as long as a correction is made.
                self.add_word_to_corrected(" ".join(self.words_list))
                return self.corrected

        self.perform_correction(" ".join(temp_words), self.correction_list, self.max_syllable)
        self.add_word_to_corrected(word_to_add)

        return self.corrected

    def build_word_syllable_list(self, keywords_library):
        temp_list = keywords_library.get_keywords_with_syllable()
        temp_list2 = [KeywordObj(std_funcs) for std_funcs in self.std_functions]
        temp_list3 = [KeywordObj(variable) for variable in self.variables_list]
            
        return list(reversed(temp_list + temp_list2 + temp_list3)) # this prioritises variables to keywords


    def build_custom_word_syllable_list(self, list_word_to_add):
        temp_list = [self.kw.get_keyword_object(word) for word in list_word_to_add]

        return temp_list
   

    # Returns true if correction has been performed and return false if no correction is performed.
    def perform_correction(self, wrong_words, keyword_list_pair, max_syllable):
        min_match = 0.78
        
        if wrong_words == "":
            return False
        
        parts = wrong_words.strip().split(" ")
        if len(parts) == 0 or (len(parts) == 1 and parts[0] == ""):
            return False

        # part_word[0] consist of one word, part_word[1] consist of 2 words etc.
        part_word = [" ".join(parts[0:i+1]) for i in range(0, min(max_syllable, len(parts)))]

        # Match wrong word with the correct keyword.
        max_sim = -1
        temp_wrong_word_index = -1
        temp_correct_word = ""
        can_match_var_type = False
        can_match_char = False
        must_match_var_type = False
        can_match_keyword = True # else can match variable names.
        need_to_correct = True

        prev_word = self.query_latest_added_word()
        prev_2_words = self.query_latest_added_word(2)
        
        # This is done to ensure that variable type is matched here.
        if prev_2_words == "return type" or (prev_word == "declare" and prev_2_words != "end declare"):
            must_match_var_type = True
            can_match_var_type = True
            min_match = 0.50
        elif prev_word == "parameter":
            can_match_var_type = True
            can_match_char = True
        elif prev_word == "equal" or prev_word == "than":
            can_match_char = True

        if self.get_first_word(prev_2_words) == "declare" and prev_word in self.var_types:
            need_to_correct = False

        if prev_word == "index":
            min_match = 0.50
            can_match_keyword = False # variable name or literal must follow.

        is_same_word = False
        
        for keyword_pair in keyword_list_pair:
            if not need_to_correct: break
            
            keyword = keyword_pair.get_keyword()
            syllable = keyword_pair.get_syllable()
            # some keywords are not so common, or not so easily mispronounced,
            # they need a min sim index to allow the correction.
            # Normally, this value is 0 to signify this is not a special case.
            keyword_min_correction_value = keyword_pair.get_min_correct()
            num_part_query = min(syllable, len(parts))

            '''
                This part handles some special cases.
            '''

            if not can_match_keyword and (keyword in self.keyword_list or keyword in self.std_functions):
                # if keyword must be a variable name (not in keyword list)
                continue

            if not can_match_var_type and self.is_variable_type(keyword):
                # if keyword cannot be a variable type, skip this keyword.
                if keyword != "character" or not can_match_char:
                    continue

            if must_match_var_type and not self.is_variable_type(keyword):
                # if keyword must be a variable type and it is not, skip this keyword.
                continue

            if keyword == "function" and prev_word != "create" and prev_word != "call" and prev_word != "end":
                # 'function' must be preceeded with 'create' or 'call' or 'end' keyword
                continue

            if keyword == "type" and prev_word != "return":
                # 'type' must be preceeded with 'return'
                continue

            if (keyword == "less" or keyword == "greater") and prev_word in self.keyword_list and prev_2_words != "end function":
                # 'less' or 'greater' can only come after variable/literal/end function
                continue

            if ((int(keyword_pair.get_symbol_bits()) & 2) == 2): # get MSB from 2-bit item. Must be symbol-word
                continue

            '''
                End of special cases, start matching.
            '''

            # A word with j syllable can be matched with 1 to j wrong words.
            # Higher j is prioritised, thus the use of reversed here.
            for j in list(reversed(range(0, num_part_query))):
                curr_wrong_word = part_word[j].lower()

                if curr_wrong_word == keyword:
                    is_same_word = True
                    break

                if must_match_var_type:
                    curr_sim = sounds_like_index(curr_wrong_word, keyword, must_match=True)
                else:
                    curr_sim = sounds_like_index(curr_wrong_word, keyword)

                if curr_sim > max_sim and curr_sim > min_match and curr_sim > keyword_min_correction_value:
                    # Example: Don't correct "length with parameter integer" --> "parameter" 
                    if not self.is_part_of(curr_wrong_word, keyword):
                        max_sim = curr_sim
                        temp_wrong_word_index = j
                        temp_correct_word = keyword

            if is_same_word:
                break

        if max_sim > -1 and not is_same_word: # if there is a high similarity word.
             self.add_word_to_corrected(temp_correct_word)
             remaining_wrong_words = parts[temp_wrong_word_index+1: len(parts)]
             self.add_word_to_corrected(" ".join(remaining_wrong_words))
             return True
        else: # cannot find any match or is the same word (no need correction)
            self.add_word_to_corrected(part_word[0])
            remaining_wrong_words = parts[1: len(parts)]
            return self.perform_correction(" ".join(remaining_wrong_words), keyword_list_pair, max_syllable) or False      

    def add_word_to_corrected(self, word):
        if word is not None and word.strip() != "":
            self.corrected = "{}{}{}".format(self.corrected, self.space, word) 
            self.space = " "

    def is_part_of(self, wrong_words, keyword):
        if keyword in wrong_words.split(" "):
            return True
        else:
            return False

    def get_first_word(self, words):
        if words is None or words.strip() == "":
            return ""
        else:
            return words.split(" ")[0]
        

    def is_number(self, word):
        try:
            float(word)
            return True
        except ValueError:
            return False

    def is_variable_type(self, word):
        if word in self.var_types:
            return True
        else:
            return False
    
    def has_next_word(self):
        return len(self.words_list) > 0

    def get_next_word(self):
        if (self.has_next_word()):
            return self.words_list.pop(0).lower()

    def reinsert_word(self, word):
        self.words_list.insert(0, word)

    def query_next_word(self):
        if (self.has_next_word()):
            return self.words_list[0].lower()

    def query_latest_added_word(self, num_words=1):
        word = []
        if (self.corrected != ""):
            parts = self.corrected.split(" ")
            for i in range(len(parts) - num_words, len(parts)):
                if i >= 0 and i < len(parts):
                    word.append(parts[i])
            return " ".join(word)
