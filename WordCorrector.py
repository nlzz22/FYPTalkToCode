from num2words import num2words
from word2number import w2n
import hashlib
import re
from Keywords import Keywords, Keyword as KeywordObj
from StandardFunctions import StandardFunctions
from WordSimilarity import get_most_similar_word, sounds_like_index, get_num_syllable

class WordCorrector:
    def __init__(self, words, var_list):
        self.words_list = words.split(" ")
        self.corrected = ""
        self.space = ""
        self.var_types = ["integer", "short", "long", "float", "double", "boolean", "character", "string"]
        self.variables_list = var_list + StandardFunctions().get_std_functions()

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
            return self.words_list[index]
        else:
            return ""

    def premature_correction(self):
        list_end_constructs = ["if", "declare", "equal", "function", "for", "fall", "switch", "while"]
        
        for i in range(0, len(self.words_list)):
            # correct and -> end for end constructs.
            if self.get_word(i) == "and" and self.get_word(i+1) in list_end_constructs:
                self.words_list[i] = "end"
            # correct standard functions print f and scan f
            elif (self.get_word(i) == "print" or self.get_word(i) == "scan") and self.get_word(i+1) == "f":
                self.words_list[i] += "f"
                self.words_list[i+1] = ""
            # correct equal to -> equal two if "to" is not a variable
            elif self.get_word(i) == "equal" and self.get_word(i+1) == "to":
                if "to" not in self.variables_list:
                    self.words_list[i+1] = "two"
            # correct ii if needed
            elif self.get_word(i) == "ii":
                if "i" in self.variables_list:
                    self.words_list[i] = "i"
                elif "second" in self.variables_list:
                    self.words_list[i] = "second"
            # correct common error: condition is equal --> condition i equal
            elif self.get_word(i) == "condition" and self.get_word(i+1) == "is" and self.get_word(i+2) == "equal":
                if "i" in self.variables_list and "is" not in self.variables_list:
                    self.words_list[i+1] = "i"

    def correct_words(self):
        kw = Keywords()
        max_syllable = kw.get_max_num_syllable()
        keyword_list = kw.get_keywords()
        word_syllable_list = self.build_word_syllable_list(kw)
        temp_words = ""
        word_to_add = ""
        to_do_correction = False

        self.premature_correction()

        if self.has_next_word():
            if self.query_next_word() == "declare":
                # declaring variables does not trigger correction
                self.corrected = " ".join(self.words_list)
                return self.corrected
            elif len(self.words_list) >= 2 and self.words_list[0] == "create" and self.words_list[1] == "function":
                # create function does not trigger correction
                self.corrected = " ".join(self.words_list)
                return self.corrected
        
        # perform the correction        
        while (self.has_next_word()):
            is_string_encountered = False
            is_char_encountered = False
            current_word = self.get_next_word()
            
            if (self.is_number(current_word)):
                # Convert numbers to words (e.g. 42 -> forty-two)
                number_in_word_form = num2words(int(current_word))
                word_to_add = number_in_word_form
                to_do_correction = True
            elif (current_word == "string"):
                # do not correct strings
                word_to_add = current_word
                to_do_correction = True
                is_string_encountered = True
            elif (current_word == "character"):
                # do not correct characters
                word_to_add = current_word
                to_do_correction = True
                is_char_encountered = True
            elif (current_word in self.variables_list or current_word in keyword_list or current_word in w2n.american_number_system):
                # do not correct any variables or keywords (including numbers)
                word_to_add = current_word
                to_do_correction = True
            else:
                # wrong words to perform correction
                temp_words += current_word + " "
                to_do_correction = False
                
            if to_do_correction:
                self.perform_correction(temp_words, word_syllable_list, max_syllable)
                self.add_word_to_corrected(word_to_add)
                word_to_add = ""
                temp_words = ""

            if is_string_encountered:
                is_string_encountered = False
                words_yet_to_add = " ".join(self.words_list)
                index_end_string = words_yet_to_add.index("end string")
                if index_end_string == -1: # no end string found.
                    self.add_word_to_corrected(words_yet_to_add)
                    break
                else: # end string found
                    self.add_word_to_corrected(words_yet_to_add[0: index_end_string + 10])
                    self.words_list = words_yet_to_add[index_end_string + 10:].split(" ")
            elif is_char_encountered:
                is_char_encountered = False
                next_word = self.get_next_word()
                self.add_word_to_corrected(next_word)

        self.perform_correction(temp_words, word_syllable_list, max_syllable)
        self.add_word_to_corrected(word_to_add)

        return self.corrected

    def build_word_syllable_list(self, keywords_library):
        temp_list = keywords_library.get_keywords_with_syllable()
        for variable in self.variables_list:
            
            temp_list.append(KeywordObj(variable))
        return temp_list
            

    def perform_correction(self, wrong_words, keyword_list_pair, max_syllable):
        if wrong_words == "":
            return
        
        parts = wrong_words.strip().split(" ")
        if len(parts) == 0 or (len(parts) == 1 and parts[0] == ""):
            return

        part_word = []
        # part_word[0] consist of one word, part_word[1] consist of 2 words etc.
        for i in range(0, min(max_syllable, len(parts))):
            part_word.append(" ".join(parts[0:i+1]))

        # Match wrong word with the correct keyword.
        max_sim = -1
        temp_wrong_word_index = -1
        temp_correct_word = ""
        
        for keyword_pair in keyword_list_pair:
            keyword = keyword_pair.get_keyword()
            syllable = keyword_pair.get_syllable()
            num_part_query = min(syllable, len(parts))

            # A word with j syllable can be matched with 1 to j wrong words.
            for j in range(0, num_part_query):
                curr_wrong_word = part_word[j]
                curr_sim = sounds_like_index(curr_wrong_word, keyword)

                if curr_sim > max_sim and curr_sim > 0.75:
                    max_sim = curr_sim
                    temp_wrong_word_index = j
                    temp_correct_word = keyword

        if max_sim > -1: # if there is a high similarity word.
             self.add_word_to_corrected(temp_correct_word)
             remaining_wrong_words = parts[temp_wrong_word_index+1: len(parts)]
             self.perform_correction(" ".join(remaining_wrong_words), keyword_list_pair, max_syllable)
        else: # cannot find any match.
            self.add_word_to_corrected(part_word[0])
            remaining_wrong_words = parts[1: len(parts)]
            self.perform_correction(" ".join(remaining_wrong_words), keyword_list_pair, max_syllable)        

    def add_word_to_corrected(self, word):
        self.corrected += self.space + word
        self.space = " "

    def is_number(self, word):
        try:
            int(word)
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

    def query_latest_added_word(self):
        if (self.corrected != ""):
            parts = self.corrected.split(" ")
            return parts[len(parts) - 1]
