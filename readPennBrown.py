## siyguo@indiana.edu
## May,2013

import glob
import os
import re

## use data from /Volumes/Data/en/penntreebankv3/tagged/pos/brown
## convert brown corpus into a format, where
## each line is a pair of word and tag separated by a tab

os.chdir("your working directory")
allFileNames = []
for path in glob.glob("/your corpora path/pennbrown/c*"):
    allFileNames += glob.glob(path+"/c*")

trainFileNames = allFileNames[:450]
testFileNames = allFileNames[450:]

def convertPennBrown(FileNames, outfilename, showtag=True):
    fout = open(outfilename, 'w')
    for fin in FileNames:
        for line in open(fin, 'r'):
            line = line.strip()
            if line and not line.startswith('*'):
                if line.startswith('=='):
                    fout.write('\n\n\n')
                else:
                    if line.startswith('['):
                        line = re.subn(r'(^\[ *|\] *$)','',line)[0]
                    if line:
                        pairs = line.split(' ')
                        for pair in pairs:
                            temp = pair.split('/')
                            if len(temp) == 2:
                                word = temp[0]
                                tag = re.subn(r'\|.+$','',temp[1])[0]
                                if showtag == True:
                                    fout.write(word+'\t'+tag+'\n')
                                else:
                                    fout.write(word+'\n')
    fout.close()

convertPennBrown(testFileNames, 'test_key')
convertPennBrown(testFileNames, 'test', False)
convertPennBrown(trainFileNames, 'train')
convertPennBrown(trainFileNames, 'train_fortest', False)
