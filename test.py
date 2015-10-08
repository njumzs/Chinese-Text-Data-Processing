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

reload(sys)
sys.setdefaultencoding('utf-8')
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
                    seg_list = jieba.lcut(content_line.strip(),cut_all=False)
                    post_index += 1
                    self.post_pool[file+'_'+str(post_index)] = seg_list
                content.close()
        # 1630 post
        #print len(self.post_pool)
        self.dict_list = [key for key in jieba.dt.FREQ if not jieba.dt.FREQ[key] == 0]
        #print len(self.dict_list)


class KeywordExtrator(object):
    def __init__(self):
        self.stop_words = []

    def set_stop_words(self, stop_words_path):
        if not os.path.isfile(stop_words_path):
            raise Exception("Stop: stop word file does not exist")
        stop_content = codecs.open(stop_words_path,'rw','utf-8')
        for line in stop_content:
            self.stop_words.append(line.strip())
        stop_content.close()


class TFIDF(KeywordExtrator):
    def __init__(self,post_pool,stop_words_path,dict_list):
        KeywordExtrator.__init__(self)
        self.post_pool = post_pool
        KeywordExtrator.set_stop_words(self,stop_words_path)
        self.idf_freq = {}
        self.tf_freq = {}
        self.dict_map = {}
        self.dict_list = dict_list

    def remove_stop_words(self):
        dict_set = set([])
        for k,v in self.post_pool.items(): #k: file+post_index       v: token words list
            #print len(self.stop_words)
            words_list = [word.strip() for word in v if word.strip() not in self.stop_words]
           # print len(v)
           # print len(words_list)
            dict_set.update(words_list)
            self.post_pool[k] = words_list
        self.dict_list = list(dict_set)
        print 'dict_len'+str(len(self.dict_list))

    def __get_dict_map(self):
        for i, value in enumerate(self.dict_list):
            self.dict_map[value] = i


    def __cal_tfidf(self):
        tf_idf = {}
        #Process every single post
        #print len(self.post_pool)
        index = 0
        word_tf = {}
        for k,v in self.post_pool.items():
            print str(index)+'/'+str(len(self.post_pool))+' is computing'
            post_tfidf = {}
            word_counter = Counter(v) # get the TF
            #TF value prepared to be processed
          #  print len(word_counter)
            for word in word_counter:
                #    print word
                #print word_tf.get(word,0)
                if word_tf.get(word,0) == 0:
                    word_tf[word] = 0
                    for post_name, post_content in self.post_pool.items():
                        if word in post_content:
                            word_tf[word] += 1 # get the N
                post_tfidf[word] = round(word_counter.get(word,0.0)*math.log(len(self.post_pool)/(word_tf.get(word,0.0)+1.0)),4)
                #if not post_tfidf[word]==0:
                 #   print word+' '+str(post_tfidf[word])
            tf_idf[k] = post_tfidf
            index += 1
        return tf_idf

    def get_sparse_tfidf(self):
        self.__get_dict_map()
        tf_idf = self.__cal_tfidf()
        print 'cal tfidf over'
        sparse_tf_idf = {}
        for post_name, tfidf in tf_idf.items():
            print post_name
            word_tf_idf = {}
            for word, value in tfidf.items():
                word_tf_idf[self.dict_map.get(word,-1)] = value
                print str(self.dict_map.get(word,-1))+' '+word+' '+str(value)
            sparse_tf_idf[post_name] = word_tf_idf
        return sparse_tf_idf



if __name__ == '__main__':
    token = Tokenizer()
    token.cut_all()
    tf_idf = TFIDF(token.post_pool,'./Chinese-stop-words.txt',token.dict_list)
    tf_idf.remove_stop_words()
    tf_idf.get_sparse_tfidf()







