#!/usr/bin/env python
#encoding=utf-8
#
#
#
import sys,os
import jieba
import codecs
import jieba.analyse
#sys.path.append('../')

from optparse import OptionParser
from collections import Iterable

USAGE = "usage: python test.py [file name]"

parser = OptionParser(USAGE)
opt,args = parser.parse_args()

_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd, path))

#if len(args) < 1:
#    print USAGE
#    sys.exit(1)
data_source_dir = "./lily/"
file_list = []
post_pool = {} #dict
jieba.analyse.set_stop_words("./Chinese-stop-words.txt")

#step 1
file_list = os.listdir(data_source_dir)
for file in file_list:
    #print file
    #print os.path.isfile(data_source_dir+file)
    if os.path.isfile(data_source_dir+file):
        post_index = 0
        content = codecs.open(data_source_dir+file,'rw','utf-8')
        for content_line in content:
            #Every content_line represents a post
            #get the cut list using jieba.lcut
            seg_list = jieba.lcut(content_line,cut_all=False)
            print seg_list
            post_index += 1
            post_pool[file+'_'+str(post_index)] = seg_list
print len(post_pool)
print len(jieba.dt.FREQ)
#setp 2


class KeywordExtrator(object):
    def __init__(self):
        self.set_stop_words = []

    def set_stop_words(self, stop_words_path):
        stop_abs_path = _get_abs_path(stop_words_path)
        if not os.path.isfile(stop_abs_path):
            raise Exception("Stop: stop word file does not exist")
        stop_content = codecs.open(stop_abs_path,'rw','utf-8')
        for line in stop_content.splitlines():
            self.stop_words.add(line)


class TFIDF(KeywordExtrator):
    def __init__(self,post_pool,stop_words_path):
        self.post_pool = post_pool
        self.set_stop_words(stop_words_path)
        self.idf_freq = {}
        self.tf_freq = {}
        #jieba.dt.FREQ dict

    def remove_stop_words(self):
        for k,v in self.post_pool.items(): #k: file+post_index       v: token words list
            words_list = [word for word in v if word not in self.set_stop_words]
            self.post_pool[k] = word_list
#    def get_tfidf_perpost(self,post):
 #       for k,v in post:




