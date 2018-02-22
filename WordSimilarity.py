#!/usr/bin/env python2

import jellyfish
import pronouncing
from StandardFunctions import StandardFunctions

WEIGHT_METAPHONE = 0.35
WEIGHT_PRONOUNCING = 0.55
WEIGHT_SOUNDEX = 0.1
MIN_WEIGHT_SIM = 0.67
MIN_WEIGHT_IGNORE_OTHER = 0.9

def get_num_syllable(word):
    phones = pronouncing.phones_for_word(word)
    if len(phones) == 0:
        return 1
    else:
        return pronouncing.syllable_count(phones[0])
    
def get_phonetic_encoding_from_pronouncing(word):
    phones = pronouncing.phones_for_word(word)
    if len(phones) == 0:
        return -1
    else:
        return pronouncing.rhyming_part(phones[0])

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
    
    # jellyfish metaphone similarity
    metaphone_sim = get_sim_index(jellyfish.metaphone, jellyfish.jaro_winkler, word1encoded, word2encoded)

    # jellyfish soundex similarity
    soundex_sim = get_sim_index(jellyfish.soundex, jellyfish.jaro_winkler, word1encoded, word2encoded)

    # get phonetic encoding with pronouncing
    phonetic1b = unicode(get_phonetic_encoding_from_pronouncing(word1encoded))
    phonetic2b = unicode(get_phonetic_encoding_from_pronouncing(word2encoded))

    # pronouncing similarity
    if phonetic1b == unicode(-1) or phonetic2b == unicode(-1):
        pronounce_sim = metaphone_sim
    else:
        pronounce_sim = jellyfish.jaro_winkler(phonetic1b, phonetic2b)

    if to_print:
        print " metaphone : " + str(metaphone_sim) + ", pro : " + str(pronounce_sim) + ", soundex : " + str(soundex_sim)

    # Return sim index
    max_sim = max(max(metaphone_sim, pronounce_sim), soundex_sim)
    if max_sim >= MIN_WEIGHT_IGNORE_OTHER:
        return max_sim
    elif not must_match and (pronounce_sim < MIN_WEIGHT_SIM or metaphone_sim < MIN_WEIGHT_SIM): # soundex is not used here.
        return 0
    else:
        return WEIGHT_METAPHONE * metaphone_sim + WEIGHT_PRONOUNCING * pronounce_sim + WEIGHT_SOUNDEX * soundex_sim

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
