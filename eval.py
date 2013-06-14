## siyguo@indiana.edu
## May,2013

from HMM import *

## test
d = '/your working directory'

### Baseline
##BL_unk = HMM_Baseline(d+'train', d+'test')
##BL_unk.run_UNK()

BL_morpho = HMM_Baseline(d+'train', d+'test')
BL_morpho.run_MORPHO()

##BL_none = HMM_Baseline(d+'train', d+'test')
##BL_none.run_nnp()

### 'MORPHO'
##morpho = HMM(d+'train', d+'test')
##morpho.tagger('test_out_morpho','MORPHO')

### 'UNK'
##unk = HMM(d+'train', d+'test')
##unk.tagger('test_out_unk','UNK')

## eval
def evaluate(resultFile, keyFile):
    correct = 0
    n = 0
    fkey = open(d+keyFile,'r')
    for l in open(d+resultFile,'r'):
        n += 1
        if l == fkey.readline():
            correct += 1
    fkey.close()
    print float(correct)/n

### results
## rare words using freq<5
## no replacement in emission count
## Penn Tagset, Brown Corpus(last 50 files as testing data)
# Baseline NONE model without HMM:   0.902681728937
# Baseline UNK model without HMM:   0.902681728937
# Baseline MORPHO model without HMM:   0.902681728937
# Baseline NNP model without HMM:   0.912178183788
# UNK Trigram HMM model:    0.948608448932
# MORPHO Trigram HMM model: 0.955451559341

# This is an example sentence lacks transitional probabilities
#['They', 'were', ',', 'I', 'felt', ',', 'people', 'invariably', 'trying', 'to', 'prove', 'not', 'who', ',', 'but', 'what', 'they', 'were', ',', 'and', 'trying', 'to', 'determine', 'what', ',', 'not', 'who', ',', 'others', 'were', '.']
