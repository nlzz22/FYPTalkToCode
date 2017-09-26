
def correct_words(words):
    words_list = words.split(" ")
    corrected = ""
    space = ""

    while (has_next_word(words_list)):
        current_word = get_next_word(words_list)
        if (current_word == "reef" or current_word == "with" or current_word == "beef"):
            corrected += space + "with"
            space = " "
        elif (current_word == "intex"):
            corrected += space + "index"
            space = " "
        elif (current_word == "in"):
            # integer as in the jar, in detail, in the jail, in to jail, in the job
            next_word = query_next_word(words_list)
            if (next_word == "the" or next_word == "to"):
                get_next_word(words_list)
                next_word = query_next_word(words_list)

                if (next_word == "jar" or next_word == "jail" or next_word == "job"):
                    get_next_word(words_list)
                    corrected += space + "integer"
                    space = " "
                else:
                    corrected += space + "integer"
                    space = " "
            elif (next_word == "detail"):
                get_next_word(words_list)
                corrected += space + "integer"
                space = " "
            else:
                corrected += space + "integer"
                space = " "
        elif (current_word == "4" or current_word == "four"):
            next_word = query_next_word(words_list)
            if next_word == "loop":
                get_next_word(words_list)
                corrected += space + "for loop"
                space = " "
        elif (current_word == "and"):
            # correct and -> end only if needed
            next_word = query_next_word(words_list)
            if next_word == "if" or next_word == "declare" or next_word == "equal" or next_word == "function" or \
               next_word == "for" or next_word == "switch" or next_word == "while":
                corrected += space + "end"
                space = " "
        else:
            corrected += space + current_word
            space = " "

    return corrected
    
def has_next_word(words_list):
    return len(words_list) > 0

def get_next_word(words_list):
    if (has_next_word(words_list)):
        return words_list.pop(0).lower()

def reinsert_word(words_list, word):
    words_list.insert(0, word)

def query_next_word(words_list):
    if (has_next_word(words_list)):
        return words_list[0].lower()




words = "create function find Maximum Reef return type integer with parameter integer array numbers"
words += " with parameter integer length begin declare in the jail max equal numbers array index zero end declare"
words += " declare integer i end declare 4 loop condition i equal one condition i less than length condition i plus plus begin"
words += " if numbers array index i greater than Max"
words += " then max equal numbers array Intex i end equal end if end for loop return Max and function"
print correct_words(words)

##create function find maximum with return type integer with parameter integer array numbers with parameter integer length begin
##
##declare integer max equal numbers array index zero end declare
##	declare integer i end declare
##
##	for loop condition i equal one condition i less than length condition i plus plus begin
##
##		if numbers array index i greater than max then
##			max equal numbers array index i end equal
##		end if
##	end for loop
##
##	return max
##end function
