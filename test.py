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
                    self.post_pool[file+' '+str(post_index)] = seg_list
                content.close()
        # 1630 post
        self.dict_list = [key for key in jieba.dt.FREQ if not jieba.dt.FREQ[key] == 0]


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
            words_list = [word.strip() for word in v if word.strip() not in self.stop_words]
            dict_set.update(words_list)
            self.post_pool[k] = words_list
        self.dict_list = list(dict_set)
        print 'dict_len'+str(len(self.dict_list))

    def __get_dict_map(self):
        for i, value in enumerate(self.dict_list):
            self.dict_map[value] = i


    def __cal_tfidf(self):
        tf_idf = {}
        index = 0
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
            print str(index)+'/'+str(len(self.post_pool))+' is computing'
            post_tfidf = {}
            word_counter = Counter(v)
            for word in word_counter:
            #    print str(word_counter.get(word,0.0))+' '+str(word_doc_freq.get(word,0.0))
                post_tfidf[word] = round(word_counter.get(word,0.0)*math.log(len(self.post_pool)/(word_doc_freq.get(word,0.0)+1.0)),4)
            tf_idf[k] = post_tfidf
            index += 1
        return tf_idf

    def get_sparse_tfidf(self):
        self.__get_dict_map()
        tf_idf = self.__cal_tfidf()
        print 'cal tfidf over'
        sparse_tf_idf = {}
        for post_name, tfidf in tf_idf.items():
            word_tf_idf = {}
            for word, value in tfidf.items():
                word_tf_idf[self.dict_map.get(word,-1)] = value
            word_tf_idf_sorted = sorted(word_tf_idf.iteritems(), key=lambda d:d[0])
            sparse_tf_idf[post_name] = word_tf_idf_sorted
        sparse_tfidf_sorted = sorted(sparse_tf_idf.iteritems(), key=lambda d:d[0])
        return sparse_tfidf_sorted

    def export_2_file(self,result_dir,tfidf_result):
        for k,v in tfidf_result.items():
            post = k.split(' ')
            with open(result_dir+post[0],'w') as f:
                f.write('post '+post[1]+': ')
                for index,tfidf in v:
                    f.write('<'+str(index)+'> '+'<'+str(tfidf)+'>   ')
                f.write('\n')





if __name__ == '__main__':
    token = Tokenizer()
    print 'Step_1: Tokenizing...'
    token.cut_all()
    print 'Step_2: Delete the stop words...'
    tf_idf = TFIDF(token.post_pool,'./Chinese-stop-words.txt',token.dict_list)
    tf_idf.remove_stop_words()
    print 'Step_3: Extrat the TFIDF vector... '
    tfidf_result = tf_idf.get_sparse_tfidf()
    print 'Step_4: Export the result to specified files...'
    tf_idf.export_2_file('./result/',tfidf_result)
    print 'Conclusion: compute over'







