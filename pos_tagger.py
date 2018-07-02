# for command line usage
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--train", help='the file to train the system')
parser.add_argument("--test", help='the file to test the system')
parser.add_argument("--output", help='name of the output file')
args = parser.parse_args()

# calculate the max index given a list of probabilities
def calculate_highest_probability_index(probability_list):
    max_index = 0
    for i in range(len(probability_list)):
        if probability_list[i] > probability_list[max_index]:
            max_index = i
    return max_index


# the algorithm, when given a sentence, returns a list of tags
# to the corresponding words of the sentence.
def viterbi(sentence_to_tag, emission_table, bigram_table):
    '''
        create two lists. one list will contain the tags (tag list)
        and another list will contain the probabilities of the corresponding tags. (prob list)
        for each word in the sentence
        and then for each tag in the emission table,
        check if the word in the emission table[tag],
        if it is, then add the tag to the tag list and add the probability
        of that corresponding tag (how to find: emission[tag][word]) to the prob list.
    '''
    punctuations = ['.', ',', '(', ')', '{', '}', '[', ']', '!', '?', '"', '\'\'', '\'', '$', '&', '*', '%', '#', '@', '-', '--', '``']
    result = []
    previous_state = 'BGN'
    tokens = sentence_to_tag.split()
    for word in tokens:
        if word in punctuations:
            result.append(word)
            continue
        candidate_probabilities = []
        candidate_tags = []
        for pos_tag in emission_table:
            if word in emission_table[pos_tag]:
                candidate_probabilities.append(emission_table[pos_tag][word])
                candidate_tags.append(pos_tag)
        if len(candidate_probabilities) == 0:
            '''
                we have found an OOV here. It will simply calculate the probability
                based on the last word that is in the vocabulary (in other words, the
                word that is not OOV)
            '''
            candidate_probabilities = list(bigram_table[previous_state].values())
            candidate_tags = list(bigram_table[previous_state].keys())
            max_index = calculate_highest_probability_index(candidate_probabilities)
            most_probable_tag = candidate_tags[max_index]
            result.append(most_probable_tag)
            previous_state = most_probable_tag
            continue
        for i in range(len(candidate_probabilities)):
            #print('WORD;', word,' prev:', previous_state, " candidate_tags[i]:", candidate_tags[i], 'i:', i)
            try:
                candidate_probabilities[i] *= bigram_table[previous_state][candidate_tags[i]]
            except KeyError:
                pass
        #print('candidate probs after', candidate_probabilities)
        #print("candidte tags after", candidate_tags)
        max_index = calculate_highest_probability_index(candidate_probabilities)
        most_probable_tag = candidate_tags[max_index]
        result.append(most_probable_tag)
        previous_state = most_probable_tag

    return result


# this function uses the viterbi algorithm on a given file
# which contains just words.
def tag_corpus(file_to_tag):
    with open(file_to_tag, 'r') as file:
        data = file.readlines()
        # create an output file to write results
        with open(args.output, 'w') as out_file:
            sentence_to_tag = ""
            for line in data:
                #print(line)
                empty_line = False
                line = line.strip('\n')
                if line != '':  # keep grabbing the word until we reach an empty line.
                    sentence_to_tag += line + ' '
                    #print(sentence_to_tag)
                else:
                    empty_line = True
                    #print('end line reached')
                if empty_line: # we have the whole sentence now. let's run viterbi
                    #print("viterbi processing began")
                    #print("sentence to tag:", sentence_to_tag)
                    sentence_to_tag = sentence_to_tag.strip()
                    tags = viterbi(sentence_to_tag, emission_prob_table, bigram_prob_table)
                    tokens = sentence_to_tag.split()
                    for i in range(len(tags)):
                        output = tokens[i] + '\t' + tags[i] + '\n'
                        out_file.write(output)
                    out_file.write('\n')
                    #print('line written')
                    sentence_to_tag = "" # we are going to read a new sentence, so set it to empty
                    empty_line = False
        file.close()
        out_file.close()


# checks if the user provided all the necessary command line arguments. If not,
# lets the user know with some useful info. If the arguments are in the correct
# format successfully runs the program.
if not args.train or not args.test or not args.output:
    print('Program aborted. Please provide all the arguments for the program to run')
    print('use --help for more info')
else:
    training_file = args.train
    empty_line = 0
    state_freq_given_previous = {'BGN': {}}
    state_freq = {}
    word_freq = {}
    word_count = {}

    with open(training_file, 'r') as file:
        data = file.readlines()
        for line in data:
            if line == '\n':
                empty_line += 1
                continue
            else:
                word, pos_tag = line.split()
                if pos_tag not in word_freq:
                    word_freq[pos_tag] = {}
                else:
                    if word not in word_freq[pos_tag]:
                        word_freq[pos_tag][word] = 1
                    else:
                        word_freq[pos_tag][word] += 1
                # checking for state counts
                if pos_tag in state_freq:
                    state_freq[pos_tag] += 1
                else:
                    state_freq[pos_tag] = 1
                # checking for the word count
                if word in word_count:
                    word_count[word] += 1
                else:
                    word_count[word] = 1
    # the number of beginning tags is the total number of empty lines
    # because each sentence is delimited by an empty line in the file.
    state_freq['BGN'] = empty_line
    file.close()

    with open(training_file, 'r') as file:
        data = file.readlines()
        current_state = ""
        previous_state = "BGN"
        for i, line in enumerate(data):
            line = line.strip('\n')
            if line != '':
                word, pos_tag = line.split()
                current_state = pos_tag
                if current_state == '.':
                    continue
                if previous_state not in state_freq_given_previous:
                    state_freq_given_previous[previous_state] = {}
                else:
                    if current_state not in state_freq_given_previous[previous_state]:
                        state_freq_given_previous[previous_state][current_state] = 1
                    else:
                        state_freq_given_previous[previous_state][current_state] += 1
                previous_state = current_state
            else:
                # this means we have reached an end of sentence. there are two cases to follow:
                # previous_state becomes the last pos_tag before the period. We have to add
                # END tag with that and then change the previous tag to BGN.
                if previous_state not in state_freq_given_previous:
                    state_freq_given_previous[previous_state] = {}
                else:
                    if "END" not in state_freq_given_previous[previous_state]:
                        state_freq_given_previous[previous_state]["END"] = 1
                    else:
                        state_freq_given_previous[previous_state]["END"] += 1
                previous_state = 'BGN'
        file.close()

    # turning the frequencies to probabilities for both tables
    #  calculation for word_frequency table
    for state in word_freq:
        for word in word_freq[state]:
            word_freq[state][word] /= float(state_freq[state])

    # calculation for state_freq_given_previous table
    for previous_state in state_freq_given_previous:
        for state in state_freq_given_previous[previous_state]:
            state_freq_given_previous[previous_state][state] /= float(state_freq[previous_state])

    emission_prob_table = word_freq
    bigram_prob_table = state_freq_given_previous
    tag_corpus(args.test)
    print('Program finished successfully')






















