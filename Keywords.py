#!/usr/bin/env python2

import WordSimilarity

class Keywords:
    def __init__(self):
        list_keywords = []
        list_keywords.append(Keyword("ampersand", 3, symbol_bits=3)) # 11 in binary.
        list_keywords.append(Keyword("array", 2))
        list_keywords.append(Keyword("backslash", 2, symbol_bits=3)) # 11 in binary.
        list_keywords.append(Keyword("begin", 2))
        list_keywords.append(Keyword("call", 1))
        list_keywords.append(Keyword("character", 3))
        list_keywords.append(Keyword("colon", 2, symbol_bits=3)) # 11 in binary.
        list_keywords.append(Keyword("condition", 3))
        list_keywords.append(Keyword("create", 2))
        list_keywords.append(Keyword("declare", 2))
        list_keywords.append(Keyword("divide", 2, 0.9))
        list_keywords.append(Keyword("dollar", 2, symbol_bits=3)) # 11 in binary.
        list_keywords.append(Keyword("dot", 1, symbol_bits=3)) # 11 in binary.
        list_keywords.append(Keyword("double", 2))
        list_keywords.append(Keyword("else", 1))
        list_keywords.append(Keyword("end", 1))
        list_keywords.append(Keyword("equal", 2, symbol_bits=1)) # 01 in binary.
        list_keywords.append(Keyword("float", 1))
        list_keywords.append(Keyword("for", 1))
        list_keywords.append(Keyword("function", 2))
        list_keywords.append(Keyword("greater", 2))
        list_keywords.append(Keyword("if", 1))
        list_keywords.append(Keyword("index", 2))
        list_keywords.append(Keyword("integer", 3))
        list_keywords.append(Keyword("less", 1))
        list_keywords.append(Keyword("long", 1))
        list_keywords.append(Keyword("loop", 1))
        list_keywords.append(Keyword("minus", 2))
        list_keywords.append(Keyword("modulo", 3))
        list_keywords.append(Keyword("not", 1))
        list_keywords.append(Keyword("parameter", 4, 0.8))
        list_keywords.append(Keyword("percent", 2, symbol_bits=3)) # 11 in binary.
        list_keywords.append(Keyword("plus", 1))
        list_keywords.append(Keyword("return", 2))
        list_keywords.append(Keyword("size", 1))
        list_keywords.append(Keyword("string", 1))
        list_keywords.append(Keyword("than", 1))
        list_keywords.append(Keyword("then", 1))
        list_keywords.append(Keyword("times", 1))
        list_keywords.append(Keyword("type", 1))
        list_keywords.append(Keyword("void", 1))
        list_keywords.append(Keyword("while", 1))
        list_keywords.append(Keyword("with", 1))
        list_keywords.append(Keyword("undo", 2))
        list_keywords.append(Keyword("default", 2))
        list_keywords.append(Keyword("break", 1))
        list_keywords.append(Keyword("switch", 1))
        list_keywords.append(Keyword("case", 1, 0.8))
        list_keywords.append(Keyword("and", 1))
        list_keywords.append(Keyword("or", 1))
        list_keywords.append(Keyword("symbol", 2))
        list_keywords.append(Keyword("continue", 3))

        list_word_only = []
        max_num_syllable = -1
        for keyword in list_keywords:
            list_word_only.append(keyword.get_keyword())
            current_syllable = keyword.get_syllable()
            if current_syllable > max_num_syllable:
                max_num_syllable = current_syllable

        self.keywords = list_word_only
        self.keyword_entire = list_keywords
        self.max_syllable = max_num_syllable
    
    def get_keywords(self):
        return self.keywords

    def get_keywords_with_syllable(self):
        return self.keyword_entire

    def get_max_num_syllable(self):
        return self.max_syllable

    def get_keyword_object(self, word):
        if word in self.keywords:
            for keyword_obj in self.keyword_entire:
                if keyword_obj.get_keyword() == word:
                    return keyword_obj

        return Keyword(word)

    def get_preferred_phrases(self):
        set_keywords = set(self.get_keywords())
        phrases_list_to_add = ["declare integer", "declare string", "declare float", "declare double", "declare character", \
                                 "create function", "return type", "call function", "plus plus", \
                                 "minus minus", "end if", "end switch", "end declare", "for loop", "end equal", \
                                 "for loop condition i", "end while", "end string", "backslash", "colon", "print f", "scan f"] + \
                                 self.get_scanf_placeholders() + self.get_printf_rounding_placeholders()
        for phrase in phrases_list_to_add:
            set_keywords.add(phrase)

        return list(set_keywords)

    def get_scanf_placeholders(self):
        list_placeholders_scanf = []
        SYMBOL_PERCENT = "symbol percent "
        list_placeholders_scanf.append(SYMBOL_PERCENT + "d") # %d for int
        list_placeholders_scanf.append(SYMBOL_PERCENT + "f") # %f for float
        list_placeholders_scanf.append(SYMBOL_PERCENT + "c") # %c for char
        list_placeholders_scanf.append(SYMBOL_PERCENT + "s") # %d for char strings
        list_placeholders_scanf.append(SYMBOL_PERCENT + "lf") # %d for double

        return list_placeholders_scanf

    def get_printf_rounding_placeholders(self):
        list_placeholders_printf = []
        list_decimal_place = range(1, 10)
        PERCENT_DOT = "symbol percent symbol dot "

        # for float
        for num in list_decimal_place:
            list_placeholders_printf.append(PERCENT_DOT + str(num) + "f") # %.2f (for all the numbers from 1-9)
        # for double
        for num in list_decimal_place:
            list_placeholders_printf.append(PERCENT_DOT + str(num) + "lf") # %.2lf (for all the numbers from 1-9)

        return list_placeholders_printf

class Keyword:
    # symbol_bits consist of 2 bits, 1st bit (MSB) for must be a symbol-word, 2nd bit (LSB) for can be a symbol-word
    def __init__(self, keyword, syllable = -1, min_correct = 0, symbol_bits = 0):
        self.keyword = keyword

        if syllable == -1:
            self.syllable = WordSimilarity.get_num_syllable(keyword)
        else:
            self.syllable = syllable

        self.min_correct = min_correct
        self.symbol_bits = symbol_bits

    def get_keyword(self):
        return self.keyword

    def get_syllable(self):
        return self.syllable

    def get_min_correct(self):
        return self.min_correct

    def get_symbol_bits(self):
        return self.symbol_bits

