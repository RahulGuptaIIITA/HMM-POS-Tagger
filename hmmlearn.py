import sys


class HMMLearn:
    
    def __init__(self):
        
        # variables to keep the word/tags and tag/tag
        self.tag_tag_dict = dict()
        self.word_tag_dict= dict()

        # variables to keep the counts
        self.unique_tags_count_dict = dict()
        
        # variables to keep the probabilities
        self.emission_probabilities = dict()
        self.transition_probabilities = dict()
        
        return

    def calculate_probabilities(self):
        
        # emission probability
        for key, value in self.word_tag_dict.iteritems():
            var_array = key.split("/")
            tag = var_array[-1]
            self.emission_probabilities[key] = value / float(self.unique_tags_count_dict[tag])
        
        # transition probability
        for key, value in self.tag_tag_dict.iteritems():
            prev_tag = key.split("/")[0]
            exclude_tag = prev_tag + "/<~s>"
            exclude_prob = self.tag_tag_dict[exclude_tag] if exclude_tag in self.tag_tag_dict else 0
            self.transition_probabilities[key] = (1+value) / float(len(self.unique_tags_count_dict) + self.unique_tags_count_dict[prev_tag] - exclude_prob)
            
        return

    def save_model(self):
        file_object = open("hmmmodel.txt", "w")
    
        for string, prob in self.emission_probabilities.iteritems():
            file_object.write("em " + string + " " + str(prob))
            file_object.write("\n")
    
        for string, prob in self.transition_probabilities.iteritems():
            file_object.write("tr " + string + " " + str(prob))
            file_object.write("\n")
    
        for tag, count in self.unique_tags_count_dict.iteritems():
            exclude_count = 0
            if tag + "/<~s>" in self.tag_tag_dict:
                exclude_count = self.tag_tag_dict[tag + "/<~s>"]
            file_object.write("tg " + tag + " " + str(count - exclude_count))
            file_object.write("\n")
            
        file_object.close()
    
        return
    
    def parse_sentence(self, sentence):
        
        previous = "<s>"
        previous = previous.strip()
        if previous not in self.unique_tags_count_dict:
            self.unique_tags_count_dict[previous] = 0
        self.unique_tags_count_dict[previous] += 1
        
        word_tags = sentence.split(" ")
        
        for i, word_tag in enumerate(word_tags):
            word_tag = word_tag.strip()
            var_array = word_tag.split("/")
            tag = var_array[-1]
            tag = tag.strip()
            
            if tag not in self.unique_tags_count_dict:
                self.unique_tags_count_dict[tag] = 0
            self.unique_tags_count_dict[tag] += 1
            
            if word_tag not in self.word_tag_dict:
                self.word_tag_dict[word_tag] = 0
            self.word_tag_dict[word_tag] += 1
            
            if previous + "/" + tag not in self.tag_tag_dict:
                self.tag_tag_dict[previous + "/" + tag] = 0
            self.tag_tag_dict[previous + "/" + tag] += 1
            
            previous = tag
        
        if previous + "/<~s>" not in self.tag_tag_dict:
            self.tag_tag_dict[previous + "/<~s>"] = 0
        self.tag_tag_dict[previous + "/<~s>"] += 1
        
        return
    
    def run(self, infile):
        try:
            with open(infile) as file:
                sentences = file.readlines()
                for sentence in sentences:
                    self.parse_sentence(sentence)
            
            self.calculate_probabilities()
            self.save_model()
            
        except Exception as e:
            print e
            
        return


if __name__ == "__main__":
    infile = sys.argv[1]
    hmm_learn_object = HMMLearn()
    hmm_learn_object.run(infile)
