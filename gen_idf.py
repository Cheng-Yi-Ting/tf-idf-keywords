#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import math
import re
import codecs
import re
import jieba
import json
import os
import datetime
import sys, getopt

from segmenter import segment
FOLDER_NAME='data'
jieba.load_userdict(FOLDER_NAME+'/dict.txt') 

class MyDocuments(object):    # memory efficient data streaming
    def __init__(self, dirname):
        self.dirname = dirname
        self.fname=[]
        for dirfile in os.walk(self.dirname):
            self.folderName = dirfile[0]#資料夾名
            for fname in dirfile[2]: #檔名
                self.fname.append(fname)
            break
        # print(FOLDER_NAME)
        # print(self.fname)
            # FOLDER_NAME = self.dirname
        # FILE_DIR = os.path.join(os.path.split(os.path.realpath(__file__))[0], FOLDER_NAME)
        # self.docs = self.read_file(FILE_DIR + '/' + dirname, 'json')

        if not os.path.isdir(dirname):
            print(dirname, '- not a directory!')
            sys.exit()

    def read_file(self, path, type):
        # file.read([size])从文件读取指定的字节数，如果未给定或为负则读取所有。
        if type == 'json':
            with open(path, 'r', encoding='utf-8') as file:
                data = json.loads(file.read())
        elif type == 'txt':
            with open(path, 'r', encoding='utf-8') as file:
                data = file.read()
        return data


    def __iter__(self):
        # os.walk() 遞迴印出資料夾中所有目錄及檔名
        # ('idf', [], ['1.txt', '2.txt'])
        # dirfile[2] =>檔名
        for fname in self.fname:
            # 內文
            docs = self.read_file(self.folderName + '/' + fname, 'json')
            for i in range(len(docs)):
                yield segment(docs[i]['content'])
            # text = open(os.path.join(self.folderName, fname),
            #             'r', encoding='utf-8', errors='ignore').read()


def main(argv):   # idf generator
    # argv=['-i', 'a.txt', '-o', 'b.txt']

    inputdir = ''
    outputfile = ''

    usage = 'usage: python gen_idf.py -i <inputdir> -o <outputfile>'
    # if len(argv) < 4:
    #     print(usage)
    #     sys.exit()
    try:
         # 处理所使用的函数叫getopt() ，因为是直接使用import 导入的getopt 模块，所以要加上限定getopt 才可以。 
        #  调用getopt 函数。函数返回两个列表：opts 和args 。opts 为分析出的格式信息。args 为不属于格式信息的剩余的命令行参数。opts 是一个两元组的列表。每个元素为：( 选项串, 附加参数) 。如果没有附加参数则为空串'' 。
        # h 后面有冒号：表示后面带参数
        # ["idir=","ofile="] idir和ofile后面有等号=，表示后面带参数
        #  $python gen_idf.py -i a.txt -o b.txt
        # opts = [('-i', 'a.txt'), ('-o', 'b.txt')]
        # opts, args = getopt.getopt(argv,"hi:o:",["idir=","ofile="])
        opts, args = getopt.getopt(argv,"-h-i:-o:",["help","idir=","ofile="])
        # print(opts)
        # print(args)
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:   # parsing arguments
        # print(arg)
        # print(arg)
        if opt in ('-h','--help'):
            print(usage)
            sys.exit()
        elif opt in ("-i", "--idir"):
            inputdir = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    documents = MyDocuments(inputdir)

    # ignored = {'', ' ', '', '。', '：', '，', '）', '（', '！', '?', '”', '“'}
    id_freq = {}
    i = 0
    # words_set=set()
    '''
    ['中共中央政治局', '委员', '中央军委', '主席', '许其亮', '主持会议', '绝大多数', '犯罪分子', '贪污', '所得', '全部', '追缴']

    ['中共中央政治局', '委员', '飞机', '现在', '变得', '越来越', '复杂', '其余', '判处', '罚金']
    '''
    for doc in documents:
        # print(doc)
        # print(len(doc))
        '''
        doc = set(x for x in doc)
        同
        words_set=set()#每篇的關鍵字
        for x in doc:
            words_set |= {x}
        '''
        doc = set(x for x in doc)
        
        for x in doc:
            id_freq[x] = id_freq.get(x, 0) + 1#統計關鍵字出現在幾篇文章
        
        if i % 1000 == 0:
            print('Documents processed: ', i, ', time: ',
                datetime.datetime.now())
        i += 1
    # print(id_freq)
    with open(outputfile, 'w', encoding='utf-8') as f:
        for key, value in id_freq.items():
            f.write(key + ' ' + str(math.log(i / value, 2)) + '\n')


if __name__ == "__main__":
    # 使用sys.argv[1:] 过滤掉第一个参数（它是执行脚本的名字，不应算作参数的一部分）。
   main(sys.argv[1:])
