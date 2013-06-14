## siyguo@indiana.edu
## May,2013

from collections import defaultdict
import sys
import re

class HMM():

    def __init__(self, trainFileName, testFileName):
        self.ftrain = trainFileName
        self.ftest = testFileName

    def get_counts(self): # get counts for deriving parameters
        self.wordtag = defaultdict(int) # emission freqs
        self.unitag = defaultdict(int) # unigram freqs of tags
        self.bitag = defaultdict(int) # bigram freqs of tags
        self.tritag = defaultdict(int) # trigram freqs of tags
        
        tag_penult = ''
        tag_last = ''
        tag_current = ''
        
        for l in open(self.ftrain, 'r'):
            l = l.strip()
            if not l:
                tag_penult = tag_last
                tag_last = tag_current
                tag_current = ''
                # update sentence boundary case
                if tag_last != '' and tag_penult != '':
                    # update bitag freqs
                    self.bitag[(tag_last, tag_current)] += 1
                    # update tritag freqs
                    self.tritag[(tag_penult, tag_last, tag_current)] += 1
            else:
                word, tag = l.split('\t')
                tag_penult = tag_last
                tag_last = tag_current
                tag_current = tag
                # update emission freqs
                self.wordtag[(word,tag)] += 1
                # update unitag freqs
                self.unitag[tag] += 1
                # update bitag freqs
                self.bitag[(tag_last, tag_current)] += 1
                # update tritag freqs
                self.tritag[(tag_penult, tag_last, tag_current)] += 1
                # update starting bigrams
                if tag_last == '' and tag_penult == '':
                    self.bitag[('','')] += 1

    def get_e(self,word,tag):
        return float(self.wordtag[(word,tag)])/self.unitag[tag]

    def get_q(self,tag_penult, tag_last, tag_current):
        return float(self.tritag[(tag_penult, tag_last, tag_current)])/self.bitag[(tag_penult, tag_last)]

    def get_parameters(self, method='UNK'): # derive parameters from counts
        self.words = set([key[0] for key in self.wordtag.keys()])
        if method == 'UNK':
            self.UNK()
        elif method == 'MORPHO':
            self.MORPHO()
        self.words = set([key[0] for key in self.wordtag.keys()])
        self.tags = set(self.unitag.keys())
        self.E = defaultdict(int)
        self.Q = defaultdict(int)
        for (word,tag) in self.wordtag:
            self.E[(word,tag)] = self.get_e(word,tag)
        for (tag_penult, tag_last, tag_current) in self.tritag:
            self.Q[(tag_penult, tag_last, tag_current)] = self.get_q(tag_penult, tag_last, tag_current)

    def tagger(self, outFileName, method='UNK'):
        # train
        sys.stderr.write("get_counts\n")
        self.get_counts()
        sys.stderr.write("get_parameters\n")
        self.get_parameters(method)
        # begin tagging
        self.sent = []
        fout = open(outFileName, 'w')
        for l in open(self.ftest, 'r'):
            l = l.strip()
            if not l:
                if self.sent:
                    sys.stderr.write("generate path for "+str(self.sent)+'\n')
                    path = self.viterbi(self.sent, method)
                    print path
                    for i in range(len(self.sent)):
                        fout.write(self.sent[i]+'\t'+path[i]+'\n')
                    self.sent = []
                fout.write('\n')
            else:
                self.sent.append(l)
        fout.close()

    def viterbi(self,sent,method='UNK'):
        V = {}
        path = {}
        # init
        V[0,'',''] = 1
        path['',''] = []
        # run
        #sys.stderr.write("entering k loop\n")
        for k in range(1,len(sent)+1):
            temp_path = {}
            word = self.get_word(sent,k-1)
            ## handling unknown words in test set using low freq words in training set
            if word not in self.words:
                print word
                if method=='UNK':
                    word = '<UNK>'
                elif method == 'MORPHO':
                    word = self.subcategorize(word)
            #sys.stderr.write("entering u loop "+str(k)+"\n")
            for u in self.get_possible_tags(k-1):
                #sys.stderr.write("entering v loop "+str(u)+"\n")
                for v in self.get_possible_tags(k):
                    V[k,u,v],prev_w = max([(V[k-1,w,u] * self.Q[w,u,v] * self.E[word,v],w) for w in self.get_possible_tags(k-2)])
                    temp_path[u,v] = path[prev_w,u] + [v]
            path = temp_path
        # last step
        prob,umax,vmax = max([(V[len(sent),u,v] * self.Q[u,v,''],u,v) for u in self.tags for v in self.tags])
        return path[umax,vmax]

    def get_possible_tags(self,k):
        if k == -1:
            return set([''])
        if k == 0:
            return set([''])
        else:
            return self.tags

    def get_word(self,sent,k):
        if k < 0:
            return ''
        else:
            return sent[k]

    def UNK(self):
        new = defaultdict(int)
        # change words with freq <5 into unknown words "<UNK>"
        for (word,tag) in self.wordtag:
            new[(word,tag)] = self.wordtag[(word,tag)]
            if self.wordtag[(word,tag)] < 5:
                new[('<UNK>',tag)] += self.wordtag[(word,tag)]
        self.wordtag = new

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


## baseline model, choosing the tag that maximizes emission probability
class HMM_Baseline(HMM):

    def run_UNK(self):
        self.get_counts()
        self.get_parameters()
        fout = open('test_out_baseline_UNK', 'w')
        best = {}
        # best tag for "<UNK>"
        pivot = 0
        besttag = ''
        for (word,tag) in self.E:
            if word == '<UNK>':
                if self.E[(word,tag)] > pivot:
                    pivot = self.E[(word,tag)]
                    besttag = tag
        best['<UNK>'] = besttag
        print '<UNK>',besttag
        i = 0 #counter, to visualize progress
        for l in open(self.ftest, 'r'):
            w = l.strip()
            if w:
                if w in best:
                    fout.write(w+'\t'+best[w]+'\n')
                else:
                    pivot = 0
                    besttag = ''
                    if w not in self.words:
                        fout.write(w+'\t'+best['<UNK>']+'\n')
                    else:
                        for (word,tag) in self.E:
                            if word == w:
                                if self.E[(word,tag)] > pivot:
                                    pivot = self.E[(word,tag)]
                                    besttag = tag
                        best[w] = besttag
                        fout.write(w+'\t'+besttag+'\n')
            else:
                fout.write('\n')
            i += 1
            if i%10000 == 0: print i
        fout.close()

    def run_MORPHO(self):
        self.get_counts()
        self.get_parameters('MORPHO')
        fout = open('test_out_baseline_MORPHO', 'w')
        best = {}
        # best tag for MORPHO rare word markers
        pivot = 0
        besttag = ''
        raremarkers = ['<PUNCS>','<CAPITAL>','<NUM>','<NOUNLIKE>','<VERBLIKE>','<JJLIKE>','<OTHER>']
        for raremarker in raremarkers:
            for (word,tag) in self.E:
                if word == raremarker:
                    if self.E[(word,tag)] > pivot:
                        pivot = self.E[(word,tag)]
                        besttag = tag
            best[raremarker] = besttag
            print raremarker,besttag
        i = 0 #counter, to visualize progress
        for l in open(self.ftest, 'r'):
            w = l.strip()
            if w:
                if w in best:
                    fout.write(w+'\t'+best[w]+'\n')
                else:
                    pivot = 0
                    besttag = ''
                    if w not in self.words:
                        fout.write(w+'\t'+best[self.subcategorize(word)]+'\n')
                    else:
                        for (word,tag) in self.E:
                            if word == w:
                                if self.E[(word,tag)] > pivot:
                                    pivot = self.E[(word,tag)]
                                    besttag = tag
                        best[w] = besttag
                        fout.write(w+'\t'+besttag+'\n')
            else:
                fout.write('\n')
            i += 1
            if i%10000 == 0: print i
        fout.close()

    def run_nnp(self):
        # tag unknown words as NNP
        self.get_counts()
        self.get_parameters('NONE')
        fout = open('test_out_baseline_nnp', 'w')
        best = {}
        i = 0 #counter, to visualize progress
        for l in open(self.ftest, 'r'):
            w = l.strip()
            if w:
                if w in best:
                    fout.write(w+'\t'+best[w]+'\n')
                else:
                    pivot = 0
                    besttag = ''
                    if w not in self.words:
                        fout.write(w+'\t'+'NONE'+'\n')
                    else:
                        for (word,tag) in self.E:
                            if word == w:
                                if self.E[(word,tag)] > pivot:
                                    pivot = self.E[(word,tag)]
                                    besttag = tag
                        best[w] = besttag
                        fout.write(w+'\t'+besttag+'\n')
            else:
                fout.write('\n')
            i += 1
            if i%10000 == 0: print i
        fout.close()
