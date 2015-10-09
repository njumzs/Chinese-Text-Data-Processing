#!/usr/bin/env python
#-*- coding=utf-8 -*-
############################################################################
#Author:        Zhanshuai Meng                                             #
#Created:       26 Sept 2015                                               #
#Last Modified: 9 Oct 2015                                                 #
#Version:   1.0                                                            #
#Description: Tokenize posts from Lily BBS of NJU with help of jieba.    #
#             Extract TF-IDF features.                                     #
############################################################################
import sys,os
import jieba
import codecs
import math
import shutil
import time
sys.path.append('../')

from optparse import OptionParser
from collections import Iterable, Counter

#Set the dedault encode as 'UTF-8'
reload(sys)
sys.setdefaultencoding('utf-8')
USAGE = "usage: python test.py [file name]"

parser = OptionParser(USAGE)
opt,args = parser.parse_args()

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd, path))

DEFAULT_SOURCE_DIR = "./lily/"

#he class to do the tokenization job
class Tokenizer():
    def __init__(self, data_source_dir=DEFAULT_SOURCE_DIR):
        self.data_source_dir = data_source_dir
        self.file_list = os.listdir(self.data_source_dir)
        self.post_pool = {}
        #self.dict_list = []
    #accomplish the tokenization job using jieba
    def cut_all(self):
        for file in self.file_list:
         #   print file
            if os.path.isfile(self.data_source_dir+file):
                post_index = 0
                content = codecs.open(self.data_source_dir+file,'rw','utf-8')
                for content_line in content:
                    #Every content_line represents a post
                    #get the cut list using jieba.lcut
                    #print content_line
                    seg_list = jieba.lcut(content_line.strip(),cut_all=False)
                    post_index += 1
                    post_index_str = str(post_index)
                    if post_index <= 9:
                        post_index_str = '00'+str(post_index)
                    elif post_index <= 99:
                        post_index_str = '0'+str(post_index)
                    self.post_pool[file+' '+post_index_str] = seg_list
                content.close()
       # self.dict_list = [key for key in jieba.dt.FREQ if not jieba.dt.FREQ[key] == 0]

#Extract the key words, initialize the stop word list
class KeywordExtractor(object):
    def __init__(self):
        self.stop_words = []

    def set_stop_words(self, stop_words_path):
        if not os.path.isfile(stop_words_path):
            raise Exception("Stop: stop word file does not exist")
        stop_content = codecs.open(stop_words_path,'rw','utf-8')
        for line in stop_content:
            self.stop_words.append(line.strip())
        stop_content.close()

#delete the stop words and generate the TFIDF vector
class TFIDF(KeywordExtractor):
    def __init__(self,post_pool,stop_words_path):
        KeywordExtractor.__init__(self)
        self.post_pool = post_pool
        KeywordExtractor.set_stop_words(self,stop_words_path)
        self.idf_freq = {}
        self.tf_freq = {}
        self.dict_map = {}
        self.dict_list = {}

    def remove_stop_words(self):
        dict_set = set([])
        for k,v in self.post_pool.items(): #k: file+post_index       v: token words list
            words_list = [word.strip() for word in v if word.strip() not in self.stop_words]
            dict_set.update(words_list)
            self.post_pool[k] = words_list
        self.dict_list = list(dict_set)
        #print 'dict_len'+str(len(self.dict_list))

    #generate the dict word-index map
    def __get_dict_map(self):
        for i, value in enumerate(self.dict_list):
            self.dict_map[value] = i


    def __cal_tfidf(self):
        tf_idf = {}
        #index = 0
        word_doc_freq = {}
        for k,v in self.post_pool.items():
            word_post_freq = {}
            word_counter = Counter(v) # get the TF
            #TF value prepared to be processed
            for word, counter in word_counter.items():
                if word_doc_freq.get(word,0) == 0:
                    word_doc_freq[word] = 0
                word_doc_freq[word] += 1

        for k,v in self.post_pool.items():
            #print str(index)+'/'+str(len(self.post_pool))+' is computing'
            post_tfidf = {}
            word_counter = Counter(v)
            number = len(v)
            for word in word_counter:
                post_tfidf[word] = round(((word_counter.get(word,0.0)*1.0)/number)*math.log((len(self.post_pool)*1.0)/(word_doc_freq.get(word,0.0)+1.0)),4)
            tf_idf[k] = post_tfidf
         #   index += 1
        return tf_idf

    def get_sparse_tfidf(self):
        self.__get_dict_map()
        tf_idf = self.__cal_tfidf()
        print 'calculate tfidf over'
        sparse_tf_idf = {}
        for post_name, tfidf in tf_idf.items():
            word_tf_idf = {}
            for word, value in tfidf.items():
                word_tf_idf[self.dict_map.get(word,-1)] = value
            word_tf_idf_sorted = sorted(word_tf_idf.iteritems(), key=lambda d:d[0])
            sparse_tf_idf[post_name] = word_tf_idf_sorted
        sparse_tfidf_sorted = sorted(sparse_tf_idf.iteritems(), key=lambda d:d[0])
        return sparse_tfidf_sorted

    def export_dict(self,result_dir):
        with open(result_dir+'dict_index.txt','a') as f:
            for i, value in enumerate(self.dict_list):
                f.write(str(i)+': '+value+'\n')



    def export_2_file(self,result_dir,tfidf_result):
        file_list = os.listdir(result_dir)
        #Detele any existing result files or dirs
        for per_file in file_list:
            if os.path.isfile(result_dir+per_file):
             #   if not 'dict_index' in per_file:
                os.remove(result_dir+per_file)
            elif os.path.isdir(result_dir+per_file):
                shutil.rmtree(result_dir+per_file,True)
        #generate new result files
        self.export_dict(result_dir)
        for k,v in tfidf_result:
            post = k.split(' ')
            with open(result_dir+post[0],'a') as f:
                f.write('post '+post[1].lstrip('0')+': ')
                for index,tfidf in v:
                    f.write('<'+str(index)+'>:'+'<'+str(tfidf)+'>   ')
                f.write('\n')





if __name__ == '__main__':
    start = time.clock()
    token = Tokenizer()
    print '--------Step_1: Tokenizing...-------'
    token.cut_all()
    print '--------Step_2: Delete the stop words...--------'
    tf_idf = TFIDF(token.post_pool,'./Chinese-stop-words.txt')
    tf_idf.remove_stop_words()
    print '--------Step_3: Extract the TFIDF vector...-------- '
    tfidf_result = tf_idf.get_sparse_tfidf()
    print '--------Step_4: Export the result to specified files...--------'
    tf_idf.export_2_file('../result/',tfidf_result)
    end = time.clock()
    print 'Conduction report: compute successfully in total time of %fs' % (end - start)
