#!/usr/bin/env python
#encoding=utf-8
#
#
#
import sys,os
import jieba
import codecs
import jieba.analyse
import math
#sys.path.append('../')

from optparse import OptionParser
from collections import Iterable, Counter

USAGE = "usage: python test.py [file name]"

parser = OptionParser(USAGE)
opt,args = parser.parse_args()

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd, path))

#if len(args) < 1:
#    print USAGE
#    sys.exit(1)
DEFAULT_SOURCE_DIR = "./lily/"

#step 1
class Tokenizer():
    def __init__(self, data_source_dir=DEFAULT_SOURCE_DIR):
        self.data_source_dir = data_source_dir
        self.file_list = os.listdir(self.data_source_dir)
        self.post_pool = {}
        self.dict_list = []

    def cut_all(self):
        for file in self.file_list:
            print file
            if os.path.isfile(self.data_source_dir+file):
                post_index = 0
                content = codecs.open(self.data_source_dir+file,'rw','utf-8')
                for content_line in content:
                    #Every content_line represents a post
                    #get the cut list using jieba.lcut
                    #print content_line
                    seg_list = jieba.lcut(content_line,cut_all=False)
                    post_index += 1
                    self.post_pool[file+'_'+str(post_index)] = seg_list
                content.close()
        # 1630 post
        print len(self.post_pool)
        self.dict_list = [key for key in jieba.dt.FREQ if not jieba.dt.FREQ[key] == 0]
        print len(self.dict_list)


class KeywordExtrator(object):
    def __init__(self):
        self.stop_words = []

    def set_stop_words(self, stop_words_path):
        if not os.path.isfile(stop_words_path):
            raise Exception("Stop: stop word file does not exist")
        stop_content = codecs.open(stop_words_path,'rw','utf-8')
        for line in stop_content:
            self.stop_words.append(line)
        stop_content.close()


class TFIDF(KeywordExtrator):
    def __init__(self,post_pool,stop_words_path,dict_list):
        KeywordExtrator.__init__(self)
        self.post_pool = post_pool
        KeywordExtrator.set_stop_words(self,stop_words_path)
        self.idf_freq = {}
        self.tf_freq = {}
        self.dict_list = dict_list
        #jieba.dt.FREQ dict

    def remove_stop_words(self):
        for k,v in self.post_pool.items(): #k: file+post_index       v: token words list
            words_list = [word for word in v if word not in self.stop_words]
            self.post_pool[k] = words_list

    def get_tfidf(self):
        tf_idf = {}
        #Process every single post
        print len(self.post_pool)
        for k,v in self.post_pool.items():
            print k
            post_tfidf = {}
            word_counter = Counter(v) # get the TF
            #TF value prepared to be processed
            print len(word_counter)
            print len(self.dict_list)
            for word in self.dict_list:
                #    print word
                post_tfidf[word] = 0
                for post_name, post_content in self.post_pool.items():
                    if word in post_content:
                        post_tfidf[word] += 1 # get the N
                post_tfidf[word] = word_counter.get(word,0.0)*math.log(len(self.post_pool)/(post_tfidf.get(word,0.0)+1.0))
                if not post_tfidf[word]==0:
                    print word+' '+str(post_tfidf[word])+'\n'
            tf_idf[k] = post_tfidf
        return tf_idf



g = Tokenizer()
g.cut_all()

tf_idf = TFIDF(g.post_pool,'./Chinese-stop-words.txt',g.dict_list)
tf_idf.remove_stop_words()
tf_idf.get_tfidf()
#for k,v in tf_idf.get_tfidf().items():
    #print 'File: '+k
 #   for word, value in v.items():
  #      print word+' '+str(value)+'\n'





