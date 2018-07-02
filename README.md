### How to run the program:

This python program utilizes command line arguments. You need to provide three flags and arguments along with it. The Flags are as follows:

+ --train [the name of the training file]
+ --test [the name of the file to test the system]
+ --output [the output file that will be produced after the program executes successfully]

Here's the exact command I used to run the program:

**python pos_tagger.py --train training_file.pos --test WSJ_23.words --output ma3599.pos**

### How I dealt with OOV (Out of Vocabulary words):

In order to detect an OOV, I checked if the list of potential probabilities is empty.
Then I populated the probabilities list based on the previous state which contains a valid
tag. To be more technical, I used bigram_table[previous_state].values(). Then I used another
function to pick the **index** of highest probability from the list and use the index to find
the corresponding tag from the tag list (called candidate_tags in the program).
