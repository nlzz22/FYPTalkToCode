#!/usr/bin/env python2

import jellyfish
import pronouncing
from StandardFunctions import StandardFunctions


##WEIGHT_METAPHONE = 0.35
##WEIGHT_PRONOUNCING = 0.55
##WEIGHT_SOUNDEX = 0.1
##MIN_WEIGHT_SIM = 0.67
##MIN_WEIGHT_IGNORE_OTHER = 0.9
MIN_WEIGHT_PRONOUNCING = 0.5
SIMILAR_FIRST_PART_MULTIPLIER = 1.1

def get_first_part(words):
    first_word = words.split(" ")[0]
    first_word_without_num = first_word.replace("0", "").replace("1", "").replace("2","")

    return first_word_without_num

def get_num_syllable(word):
    phones = pronouncing.phones_for_word(word)
    if len(phones) == 0:
        return 1
    else:
        return pronouncing.syllable_count(phones[0])

def get_phones_for_word_not_in_dict(word):
    '''
        The conversion here is based on LOGIOS Lexicon Tool (http://www.speech.cs.cmu.edu/tools/lextool.html)
        This tool generates a pronunciation dictionary from a list of (English) words.
        The Lexicon Tool uses the CMUdict dictionary along with some simple normalization and inflection rules to identify a word,
        and uses letter-to-sound rules when all else fails.
    '''

    if word == "modulo":
        return "M AA D Y UW L OW"
    elif word == "modulus":
        return "M AA D Y AH L AH S"
    elif word == "corrector":
        return "K AH R EH K T ER"
    else:
        return word.upper()
    
def get_phonetic_encodings_from_pronouncing(word):
    phones_final = ""
    separator = ""
    parts = word.split(" ")
    for part in parts:
        curr_phone = pronouncing.phones_for_word(part)
        if len(curr_phone) == 0:
            phones_final += separator + get_phones_for_word_not_in_dict(part)
        else:
            phones_final += separator + curr_phone[0]
        separator = " "

    rhyming_part = pronouncing.rhyming_part(phones_final)
        
    return phones_final, rhyming_part

def get_sim_index_pronouncing(str_compare_function, word1, word2, to_print=False):
    # get phonetic encodings
    phone1, rhyme1 = get_phonetic_encodings_from_pronouncing(word1)
    phone2, rhyme2 = get_phonetic_encodings_from_pronouncing(word2)

    if to_print:
        print "phone : " + str(phone1) + " , " + str(phone2)
        print "rhyme : " + str(rhyme1) + " , " + str(rhyme2)

    # get similarity index
    phone_sim = str_compare_function(unicode(phone1), unicode(phone2))
    if get_first_part(phone1) == get_first_part(phone2): # if first part of the phone is the same, higher sim index.
        phone_sim = min(1.0, phone_sim * SIMILAR_FIRST_PART_MULTIPLIER)
    
    rhyme_sim = str_compare_function(unicode(rhyme1), unicode(rhyme2))

    if to_print:
        print "phone sim : " + str(phone_sim)
        print "rhyme sim : " + str(rhyme_sim)

    if rhyme_sim == 1 or phone_sim == 1:
        return 1.0
    if rhyme_sim < MIN_WEIGHT_PRONOUNCING or phone_sim < MIN_WEIGHT_PRONOUNCING:
        return 0
    return max(phone_sim, rhyme_sim)    

def get_sim_index(encoding_function, str_compare_function, word1, word2):
    # get phonetic encoding
    phonetic1 = unicode(encoding_function(word1))
    phonetic2 = unicode(encoding_function(word2))
    
    # get similarity index
    sim_index = str_compare_function(phonetic1, phonetic2)

    return sim_index

def sounds_like_index(word1, word2, to_print=False, must_match=False):
    # convert from string to unicode
    word1encoded = unicode(word1)
    word2encoded = unicode(word2)

    '''
        This part is old code which uses metaphone and soundex sim index, which is no longer in use currently.
    '''
##    # jellyfish metaphone similarity
##    metaphone_sim = get_sim_index(jellyfish.metaphone, jellyfish.jaro_winkler, word1encoded, word2encoded)
##
##    # jellyfish soundex similarity
##    soundex_sim = get_sim_index(jellyfish.soundex, jellyfish.jaro_winkler, word1encoded, word2encoded)

    # get phonetic encoding with pronouncing
    pronouncing_sim = get_sim_index_pronouncing(jellyfish.jaro_distance, word1encoded, word2encoded, to_print)

    return pronouncing_sim

    '''
        This part is old code which uses weighted sum, which is no longer in use currently.
        Note: @param: must_match is no longer in use with this new algorithm.
    '''

    # Return sim index
##    max_sim = max(max(metaphone_sim, pronounce_sim), soundex_sim)
##    if max_sim >= MIN_WEIGHT_IGNORE_OTHER:
##        return max_sim
##    elif not must_match and (pronounce_sim < MIN_WEIGHT_SIM or metaphone_sim < MIN_WEIGHT_SIM): # soundex is not used here.
##        return 0
##    else:
##        return WEIGHT_METAPHONE * metaphone_sim + WEIGHT_PRONOUNCING * pronounce_sim + WEIGHT_SOUNDEX * soundex_sim

# Gets the most similar word in pronounciation to the given word from given word_list
# Example use: get_most_similar_word("eye", ["i", "numbers", "max", "length"]) returns "i"
def get_most_similar_word(word, word_list):
    max_sim_index = -1
    best_word = ""
    list_std_funcs = StandardFunctions().get_std_functions()
    word_list += list_std_funcs
    
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

if __name__ == "__main__":    
    while True:
        print "Find the similarity index between 2 words!"
        first_word = raw_input("First word: ")
        second_word = raw_input("Second word: ")
        print "Similarity index is : " + str(sounds_like_index(first_word, second_word, True))
