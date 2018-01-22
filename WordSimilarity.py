import jellyfish
import pronouncing
from StandardFunctions import StandardFunctions

WEIGHT_JELLYFISH = 0.35
WEIGHT_PRONOUNCING = 0.65
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

def sounds_like_index(word1, word2, to_print=False, must_match=False):
    # convert from string to unicode
    word1encoded = unicode(word1)
    word2encoded = unicode(word2)
    
    # get phonetic encoding with jellyfish
    phonetic1 = unicode(jellyfish.metaphone(word1encoded))
    phonetic2 = unicode(jellyfish.metaphone(word2encoded))

    jelly_sim = jellyfish.jaro_winkler(phonetic1, phonetic2)

    # get phonetic encoding with pronouncing
    phonetic1b = unicode(get_phonetic_encoding_from_pronouncing(word1encoded))
    phonetic2b = unicode(get_phonetic_encoding_from_pronouncing(word2encoded))

    if phonetic1b == unicode(-1) or phonetic2b == unicode(-1):
        pronounce_sim = jelly_sim
    else:
        pronounce_sim = jellyfish.jaro_winkler(phonetic1b, phonetic2b)

    if to_print:
        print " jellyfish : " + str(phonetic1) + ", " + str(phonetic2)
        print " pronounce : " + str(phonetic1b) + ", " + str(phonetic2b)
        print " jellyfish : " + str(jelly_sim) + ", pro : " + str(pronounce_sim)

    # Return sim index
    if pronounce_sim >= MIN_WEIGHT_IGNORE_OTHER or jelly_sim >= MIN_WEIGHT_IGNORE_OTHER:
        return max(pronounce_sim, jelly_sim)
    elif not must_match and (pronounce_sim < MIN_WEIGHT_SIM or jelly_sim < MIN_WEIGHT_SIM):
        return 0
    else:
        return WEIGHT_JELLYFISH * jelly_sim + WEIGHT_PRONOUNCING * pronounce_sim

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
