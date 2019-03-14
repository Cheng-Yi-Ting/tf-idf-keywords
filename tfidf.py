#!/usr/bin/python
# -*- coding: utf-8 -*-

from segmenter import segment
import sys, getopt
import os
import json

class MyDocuments(object):
    def __init__(self, idf_path,dirname):
        self.dirname = dirname
        self.fname=[]
        # print(idf_path)
        # print(dirname)
        for dirfile in os.walk(self.dirname):
            # print(dirfile)
            self.folderName = dirfile[0]#資料夾名
            for fname in dirfile[2]: #檔名
                self.fname.append(fname)
            break
        self.dirname = dirname
        self.idf_path = idf_path
        self.idf_freq = {}     # idf
        self.mean_idf = 0.0    # 均值
        self.load_idf()

    def load_idf(self):       # 從文件中載入IDF
        cnt = 0
        with open(self.idf_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    word, freq = line.strip().split(' ')
                    cnt += 1
                except Exception as e:
                    pass
                self.idf_freq[word] = float(freq)
        print('Vocabularies loaded: %d' % cnt)
        self.mean_idf = sum(self.idf_freq.values()) / cnt
    
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
        for fname in self.fname:
            # 內文
            docs = self.read_file(self.folderName + '/' + fname, 'json')
            for i in range(len(docs)):
                yield segment(docs[i]['title'])
                yield segment(docs[i]['content'])
            # text = open(os.path.join(self.folderName, fname),
            #             'r', encoding='utf-8', errors='ignore').read()

    def extract_keywords(self, sentence, topK=20):    # 提取關鍵詞
        # 斷詞
        seg_list = segment(sentence)
        # print(seg_list)
        freq = {}
        for w in seg_list:
            # 如果沒有找到word，設成0，再+1。如果有找到word就+1
            freq[w] = freq.get(w, 0.0) + 1.0
            freq[w]=freq[w]/len(seg_list)
        # print(seg_list)
        # print(freq)
        total = sum(freq.values())#文檔數量
        for k in freq:   # 計算 TF-IDF
            # freq[k] *= self.idf_freq.get(k, self.mean_idf) / total
            freq[k] *= self.idf_freq.get(k, self.mean_idf)
            # print(freq[k])

        
        tags = sorted(freq, key=freq.__getitem__, reverse=True)  # 排序

        if topK:
            return tags[:topK]
        else:
            return tags


def main(argv):
    idffile = ''
    document = ''
    topK = None

    usage = 'usage: python tfidf.py -i <idffile> -d <document> -t <topK>'
    if len(argv) < 4:
        print(usage)
        sys.exit()
    try:
        # opts, args = getopt.getopt(argv,"hi:d:t:",
        #     ["idffile=","document=", "topK="])
         opts, args = getopt.getopt(argv,"-h-i:-d:-t:",["help","idffile=","document=", "topK="])
        #  $python tfidf.py -i idf.txt -d test.txt -t 20
        # opts= [('-i', 'idf.txt'), ('-d', 'test.txt'), ('-t', '20')]
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    for opt, arg in opts:   # parsing arguments
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt in ("-i", "--idffile"):
            idffile = arg
        elif opt in ("-d", "--document"):
            document = arg
        elif opt in ("-t", "--topK"):
            topK = int(arg)

    documents = MyDocuments(idffile,document)

    for doc in documents:
        print(doc)
    # 讀檔
    # sentence = open(document, 'r', encoding='utf-8', errors='ignore').read()
    # tags = tdidf.extract_keywords(sentence, topK)

    # for tag in tags:
    #     print(tag)


if __name__ == "__main__":
    main(sys.argv[1:])
