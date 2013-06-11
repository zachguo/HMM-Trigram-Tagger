HMM-Trigram-Tagger
==================

A Hidden-Markov-Model Trigram Tagger (with several simple methods to deal with unseen words)

---

## (a)Specification of Project Scope

In this project, two taggers would be built from scratch: One is a trigram HMM tagger. The other one is a baseline tagger, which is implemented to compare with the performance of trigram HMM tagger.

Besides, two ways of handling unknown words would be implemented: One is UNK method, that is, using the emission probabilities of rare words to estimate the emission probabilities of unseen words. The other one is MORPHO, which is a modified version of UNK. Instead of marking all rare words as ‘UNK’, I made further subcategorization of these rare words based on certain morphological cues. MORPHO is actually inspired by Wen’s presentation and I found it could be easily incorporated into my tagger.

## (b) Description of Implementation 
### 1. Data Preparation

A Brown corpus using Penn Treebank tagset is used as my dataset. The dataset contains 500 plain text files. I use the first 450 files (ordered by file names) as training data, and the last 50 files as testing data. For the ease of analysis, all training and testing data are converted in to a format that each line is a word-tag pair separated by a tab.

### 2. Building Baseline Tagger

First, a baseline tagger is implemented to be compared with the trigram HMM. The baseline tagger just chooses the tag maximizing emission probability for a given word, no transition information is considered.
￼￼
### ￼3. Building Trigram HMM Tagger
Then, a trigram HMM tagger would be built from scratch. Based on trigram Markov assumption, the transition probability is calculated as the probability of the occurrence of a tag given its previous two tags.
Basic procedures of the trigram HMM model includes: 

> 1) Read training data;
> 2) Get counts (word-tag pair, uni-tag, bi-tag, tri-tag); 3) Estimate counts for rare words;
> 4) Calculate parameters (transition & emission probability) based on counts;
> 5) Read testing data sentence by sentence, and tag the sentence using a Viterbi algorithm. Notice that we would change the third and fifth procedures to handle unknown words.

### 4. Two methods of handling unknown words: UNK & MORPHO
There are two major methods to handle unknown words, one is UNK and the other one is MORPHO. The general ideas of the two methods are the same, that is, using the emission probabilities of rare words to estimate the emission probabilities of unseen words. In the next few paragraphs, I will describe both of them in details.

#### 4.1 UNK
Before calculating model parameters, namely, transition and emission probabilities, we will first find all words with frequency less than 5 and give them a common label ‘<UNK>’. So, we can aggregate all rare words into a same category. Then we can get the emission counts like ￼“<UNK>, NNP”. Notice that the label does not replace the original words, but it’s added into the preexist set of emission counts, as is shown in the code below:  

        def UNK(self):
            new = defaultdict(int)
            # change words with freq <5 into unknown words "<UNK>"
            for (word,tag) in self.wordtag:
                new[(word,tag)] = self.wordtag[(word,tag)]
                if self.wordtag[(word,tag)] < 5:
                    new[('<UNK>',tag)] += self.wordtag[(word,tag)]
            self.wordtag = new

When tagging a sentence, the tagger would treat all unseen words as ‘<UNK>’. Hence, every unseen word can get a non-zero emission probability.

#### 4.2 MORPHO
Basic idea of MORPHO is the same as UNK, that is, using the emission probabilities of rare words to estimate the emission probabilities of unknown words. The difference is that MORPHO uses heuristics of morphology to subcategorize these rare words into subcategories like ‘<CAPITAL>’ and ‘<NOUNLIKE>’ etc., instead of a common category ‘<UNK>’ in UNK method. The implementation is shown as below:

        def subcategorize(self,word):
            if not re.search(r'\w',word):
                return '<PUNCS>'
            elif re.search(r'[A-Z]',word):
                return '<CAPITAL>'
            elif re.search(r'\d',word):
                return '<NUM>'
            elif re.search(r'(ion\b|ty\b|ics\b|ment\b|ence\b|ance\b|ness\b|ist\b|ism\b)',word):
                return '<NOUNLIKE>'
            elif re.search(r'(ate\b|fy\b|ize\b|\ben|\bem)',word):
                return '<VERBLIKE>'
            elif re.search(r'(\bun|\bin|ble\b|ry\b|ish\b|ious\b|ical\b|\bnon)',word):
                return '<JJLIKE>'
            else:
                return '<OTHER>'
                
        def MORPHO(self):
            new = defaultdict(int)
            for (word,tag) in self.wordtag:
                new[(word,tag)] = self.wordtag[(word,tag)]
                if self.wordtag[(word,tag)] < 5:
                    new[(self.subcategorize(word),tag)] += self.wordtag[(word,tag)]
            self.wordtag = new
￼
## ￼￼(c) Evaluation of Project
We then run each tagger with both unknown words handling methods, and calculate the tagging accuracy as number of correctly tagged words divided by total number of words.

We also add a ‘do nothing’ method, in which tagger would not tag unseen words at all. So, the accuracy of a baseline tagger with ‘do nothing’ method should be the lowest among all taggers, which forms a bottom line for accuracy comparison.

Besides, a greedy method called ‘NNP’ is also implemented, in which tagger would tag all unseen words as ‘NNP’. Actually, UNK and MORPHO are in essence the same as ‘NNP’ method, in a sense that they tagged all unknown words as a same tag. The difference is that UNK and MORPHO tagged all unseen words as ‘NNPS’ instead of an arbitrary ‘NNP’ based on statistics of rare words in the training data.

Accuracies for all the taggers are shown in the following table:

| ￼￼￼￼Tagger | ￼Unknown Words Handling Method | Accuracy |
| --- | --- | --- |
| Baseline | ￼￼Do nothing | ￼0.903 |
| Baseline | ￼￼UNK | ￼0.903 |
| Baseline | ￼￼MORPHO | 0.903 |
| Baseline | ￼￼‘NNP’ | 0.912 |
| ￼Trigram HMM | ￼￼UNK | ￼0.949 |
| ￼Trigram HMM | ￼￼MORPHO | ￼0.955 |

￼￼￼￼￼￼￼￼The table shows that, for baseline tagger, UNK and MORPHO methods perform no better than doing nothing, and worse than just tagging all unseen words as ‘NNP’. None of the unknown words in testing data is originally tagged as ‘NNPS’, so UNK and MORPHO just perform like doing nothing.

For trigram HMM tagger, performances of taggers with both methods are generally better than baseline model. And subcategorizing unseen words works better than treating them as a common category.

However, when having a detailed look at the tagged results of trigram HMM tagger, I found that some sentences had no tags at all. For example, there is no unseen word in the following sentence but it is still untagged: “They were, I felt, people invariably trying to prove not who, but what they were, and trying to determine what, not who, others were.” A possible reason is that the sentence contains unseen transitions, which produces a zero transition probability. To cope the problem, smoothing should be implemented for both emission probability and transition probability. So, in the future, I will try several statistical smoothing techniques to cope with both unseen words and unseen transitions. Also, another approach worth exploring is Brown clustering algorithm, which treats all words as unseen words, and tags them in an unsupervised way.
