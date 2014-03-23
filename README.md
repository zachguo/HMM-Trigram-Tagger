HMM-Trigram-Tagger
==================

An old and super slow python implementation of HMM trigram model. It's initially created for a course assignment.

* Two taggers are included: 

  * A trigram HMM tagger;
  * A baseline tagger, which is implemented to compare with the performance of trigram HMM tagger.

* Two ways of handling unknown words would be implemented: 

  * UNK method, that is, using the emission probabilities of rare words to estimate the emission probabilities of unseen words. 
  * MORPHO method, which is a modified version of UNK. Instead of marking all rare words as ‘UNK’, I made further subcategorization of these rare words based on certain morphological cues.

* A simple accuracy evaluation:

  | ￼￼￼￼Tagger | ￼Unknown Words Handling Method | Accuracy |
  | --- | --- | --- |
  | Baseline | ￼￼Do nothing | ￼0.903 |
  | Baseline | ￼￼UNK | ￼0.903 |
  | Baseline | ￼￼MORPHO | 0.903 |
  | Baseline | ￼￼‘NNP’ | 0.912 |
  | ￼Trigram HMM | ￼￼UNK | ￼0.949 |
  | ￼Trigram HMM | ￼￼MORPHO | ￼0.955 |
