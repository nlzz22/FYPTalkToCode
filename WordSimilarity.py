import jellyfish
from StandardFunctions import StandardFunctions

def sounds_like_index(word1, word2):
    # convert from string to unicode
    word1encoded = unicode(word1)
    word2encoded = unicode(word2)
    
    # get phonetic encoding 
    phonetic1 = unicode(jellyfish.soundex(word1encoded))
    phonetic2 = unicode(jellyfish.soundex(word2encoded))
    
    return jellyfish.jaro_winkler(phonetic1, phonetic2)

def get_most_similar_word(word, word_list):
    max_sim_index = -1
    best_word = ""
    list_std_funcs = StandardFunctions().get_std_functions()
    
    for ground_word in word_list:
        if word == ground_word:
            return word

        current_sim = sounds_like_index(word, ground_word)

        # if ground word is a std function, need higher similarity index to correct.
        if ground_word in list_std_funcs and current_sim < 0.7:
            continue
        
        if current_sim > max_sim_index and current_sim > 0.5:
            max_sim_index = current_sim
            best_word = ground_word
    
    return best_word


##print get_most_similar_word("eye", ["i", "numbers", "max", "length"])
##print get_most_similar_word("lumber", ["i", "numbers", "max", "length"])
##print get_most_similar_word("next", ["i", "numbers", "max", "length"])
##print get_most_similar_word("lang", ["i", "numbers", "max", "length"])
##print get_most_similar_word("blank", ["i", "numbers", "max", "length"])
##print get_most_similar_word("makes", ["i", "numbers", "max", "length"])
