import sys
import time
from math import log10


class HMMDecode:
    
    def __init__(self):
    
        # variables to keep possible tags and words
        self.possible_tags = set()
        self.possible_words = set()
        
        # variable to keep possible tags count
        self.possible_tags_count = dict()
        
        # variables to keep the probabilities
        self.emission_probabilities = dict()
        self.transition_probabilities = dict()

        with open("hmmmodel.txt") as file:
            lines = file.readlines()
            for line in lines:
                var_array = line.split(" ")
                if var_array[0] == "em":
                    self.emission_probabilities[var_array[1]] = float(var_array[2].strip())
                    word_tag = var_array[1]
                    word = word_tag.rsplit("/")[0]
                    self.possible_words.add(word)
        
                elif var_array[0] == "tr":
                    self.transition_probabilities[var_array[1]] = float(var_array[2].strip())
        
                elif var_array[0] == "tg":
                    self.possible_tags.add(var_array[1].strip())
                    self.possible_tags_count[var_array[1]] = int(var_array[2].strip())
        return
        
    def smooth_probabilities(self, word, prev_tag, cur_tag):
        
        if (prev_tag + "/" + cur_tag) not in self.transition_probabilities:
            tr_prob = 1 / float(len(self.possible_tags) + self.possible_tags_count[prev_tag])
        else:
            tr_prob = self.transition_probabilities[prev_tag + "/" + cur_tag]
        
        if word not in self.possible_words:
            em_prob = 1
        elif (word + "/" + cur_tag) not in self.emission_probabilities:
            em_prob = 0
        else:
            em_prob = self.emission_probabilities[word + "/" + cur_tag]
            
        return em_prob, tr_prob
    
    def viterbi_algorithm(self, sentence):
        best_edge = dict()
        best_score = dict()
        words = sentence.split(" ")
        words = [word.strip() for word in words]
       
        for tag in self.possible_tags:
            em_prob, tr_prob = self.smooth_probabilities(words[0], "<s>", tag)
            best_score[(words[0], tag, 0)] = em_prob * tr_prob
            best_edge[(words[0], tag, 0)] = "<s>"

        for i in range(1, len(words)):
            for cur_tag in self.possible_tags:
                temp_score = 0
                if (words[i] in self.possible_words) and ((words[i] + "/" + cur_tag) not in self.emission_probabilities):
                    best_score[(words[i], cur_tag, i)] = temp_score
                else:
                    for prev_tag in self.possible_tags:
                        em_prob, tr_prob = self.smooth_probabilities(words[i], prev_tag, cur_tag)
                        score = best_score[(words[i-1], prev_tag, i-1)] * em_prob * tr_prob
                        best_score[(words[i], cur_tag, i)] = temp_score
                        
                        if score > temp_score:
                            temp_score = score
                            best_score[(words[i], cur_tag, i)] = score
                            best_edge[(words[i], cur_tag, i)] = prev_tag
        score = 0
        best_tag = None
        tagged_sentence = []
        nth_word = words[-1]
        words_length = len(words) - 1
        for tag in self.possible_tags:
            if best_score[(nth_word, tag, words_length)] > score:
                score = best_score[(nth_word, tag, words_length)]
                best_tag = tag
        tagged_sentence.append((nth_word, best_tag))
        
        for i in xrange(len(words) - 2, -1, -1):
            tagged_sentence.append((words[i], best_edge[(words[i+1], best_tag, i+1)]))
            best_tag = best_edge[(words[i+1], best_tag, i+1)]
            
        return tagged_sentence
    
    def tag_sentence(self, sentence, file_object):
        tagged_sentence = self.viterbi_algorithm(sentence)
        tagged_sentence = tagged_sentence[::-1]
        
        lnth = len(tagged_sentence)
        for i, word_tag in enumerate(tagged_sentence):
            word = word_tag[0]
            tag = word_tag[1]
            file_object.write(word + "/" + tag)
            if i != lnth - 1:
                file_object.write(" ")
        
        file_object.write("\n")
        
        return
    
    def run(self, infile):
        try:
            file_object = open("hmmoutput.txt", "w")
            with open(infile) as file:
                sentences = file.readlines()
                for i, sentence in enumerate(sentences):
                    self.tag_sentence(sentence, file_object)
            
            file_object.close()
            
        except Exception as e:
            print e
    
        return


if __name__ == "__main__":
    infile = sys.argv[1]
    
    hmm_decode_object = HMMDecode()
    
    start_time = time.time()
    hmm_decode_object.run(infile)
    print "total time it took {}".format(time.time() - start_time)
    
    """
    https://en.wikipedia.org/wiki/Viterbi_algorithm
    """


