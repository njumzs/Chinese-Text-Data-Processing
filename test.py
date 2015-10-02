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

USAGE = "usage: python test.py [file name]"

parser = OptionParser(USAGE)
opt,args = parser.parse_args()


#if len(args) < 1:
#    print USAGE
#    sys.exit(1)
data_source_dir = "./lily/"
file_list = []
jieba.analyse.set_stop_words("./Chinese-stop-words.txt")

file_list = os.listdir(data_source_dir)
for file in file_list:
    #print file
    #print os.path.isfile(data_source_dir+file)
    if os.path.isfile(data_source_dir+file):
        content = codecs.open(data_source_dir+file,'rw','utf-8')
        for content_line in content:
            #print content_line

            seg_list = jieba.cut(content_line,cut_all=False)
            print " ".join(seg_list)
