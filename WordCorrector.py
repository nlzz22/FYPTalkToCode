from num2words import num2words

class WordCorrector:
    def __init__(self, words):
        self.words_list = words.split(" ")
        self.corrected = ""
        self.space = ""
        self.var_types = ["integer", "short", "long", "float", "double", "boolean", "character", "string"]

    def run_correct_words_multiple(self, times):
        if (times > 0):
            self.correct_words()
            self.reinit()
            return self.run_correct_words_multiple(times - 1)
        else:
            return " ".join(self.words_list)

    def reinit(self):
        self.words_list = self.corrected.split(" ")
        self.corrected = ""
        self.space = ""

    def correct_words(self):
        while (self.has_next_word()):
            current_word = self.get_next_word()
            if (current_word == "reef" or current_word == "beef"):
                self.add_word_to_corrected("with")
            elif (current_word == "width"):
                # with (size, return type, parameter)
                next_word = self.query_next_word()
                if next_word == "size" or next_word == "parameter":
                    self.add_word_to_corrected("with")
                elif next_word == "return":
                    self.get_next_word()
                    next_word = self.query_next_word()
                    if next_word == "type":
                        self.get_next_word()
                        self.add_word_to_corrected("with return type")
                    else:
                        self.reinsert_word("return")
                        self.add_word_to_corrected("width")
                else:
                    self.add_word_to_corrected("width")
            elif (current_word == "intex"):
                self.add_word_to_corrected("index")
            elif (current_word == "in"):
                # integer 
                next_word = self.query_next_word()
                if (next_word == "the" or next_word == "to"):
                    self.get_next_word()
                    next_word = self.query_next_word()

                    if (next_word == "jar" or next_word == "jail" or next_word == "job" or next_word == "germ"):
                        self.get_next_word()
                        self.add_word_to_corrected("integer")
                    else:
                        self.add_word_to_corrected("integer")
                elif (next_word == "detail" or next_word == "danger"):
                    self.get_next_word()
                    self.add_word_to_corrected("integer")
                else:
                    self.add_word_to_corrected("integer")
            elif (current_word == "4" or current_word == "four" or current_word == "full" or current_word == "fall"):
                next_word = self.query_next_word()
                if next_word == "loop":
                    self.get_next_word()
                    self.add_word_to_corrected("for loop")
            elif (current_word == "than"):
                prev_word = self.query_latest_added_word()
                if (prev_word == "greater" or prev_word == "less"):
                    self.add_word_to_corrected(current_word)
                else:
                    self.add_word_to_corrected("then")
            elif (current_word == "and"):
                # correct and -> end only if needed
                next_word = self.query_next_word()
                if next_word == "if" or next_word == "declare" or next_word == "equal" or next_word == "function" or \
                   next_word == "for" or next_word == "fall" or next_word == "switch" or next_word == "while":
                    self.add_word_to_corrected("end")
            elif (current_word == "written"):
                next_word = self.query_next_word()
                if (next_word == "type"):
                    self.add_word_to_corrected("return")
                elif (next_word == "tie"):
                    self.get_next_word()
                    self.add_word_to_corrected("return type")
            elif (current_word == "wow" or current_word == "wild"):
                self.add_word_to_corrected("while")
            elif (current_word == "dan" or current_word == "den"):
                self.add_word_to_corrected("then")
            elif (current_word == "condition"):
                next_word = self.query_next_word()
                if (next_word == "eye"):
                    self.get_next_word()
                    self.add_word_to_corrected("condition i")
                elif (next_word == "is"):
                    self.get_next_word()
                    next_word = self.query_next_word()
                    if (next_word == "equal"):
                        # condition is equal -> condition i equal
                        self.get_next_word()
                        self.add_word_to_corrected("condition i equal")
                    else:
                        self.add_word_to_corrected("condition is")
                else:
                    self.add_word_to_corrected("condition")
            elif (current_word == "away"):
                # away -> array
                next_word = self.query_next_word()
                if (next_word == "index"):
                    self.get_next_word()
                    self.add_word_to_corrected("array index")
                else:
                    prev_word = self.query_latest_added_word()
                    if (self.is_variable_type(prev_word)):
                        self.add_word_to_corrected("array")
                    else:
                        self.add_word_to_corrected("away")
            elif (current_word == "inf"):
                self.add_word_to_corrected("i end if")
            elif (current_word == "the"):
                next_word = self.query_next_word()
                if (next_word == "game"):
                    self.get_next_word()
                    self.add_word_to_corrected("begin")
                else:
                    self.add_word_to_corrected(current_word)
            elif (current_word == "became" or current_word == "beginning"):
                self.add_word_to_corrected("begin")
            elif (current_word == "ii"):
                self.add_word_to_corrected("i")
            elif (current_word == "ecuador"):
                prev_word = self.query_latest_added_word()
                if (prev_word == "end"):
                    self.add_word_to_corrected("equal")
            elif (self.is_number(current_word)):
                # Convert numbers to words (e.g. 42 -> forty-two)
                number_in_word_form = num2words(int(current_word))
                self.add_word_to_corrected(number_in_word_form)
            else:
                self.add_word_to_corrected(current_word)

        return self.corrected

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

#wordCorrector = WordCorrector("create function find Maximum Reef return type integer with parameter integer array numbers with parameter integer length became declare integer Max equal numbers array index 0 end declare declare integer I end declare for Loop condition I equal one condition I less than blank condition I plus plus begin with numbers array index II greater than Max then makes equal numbers array index and equal and if and for Loop return Max and function ")
#print wordCorrector.run_correct_words_multiple(5)
