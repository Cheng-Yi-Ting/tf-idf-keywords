#!/usr/bin/python
# -*- coding: utf-8 -*-

from segmenter import segment
from segmenter import preprocess
import sys, getopt
import os
import json
import codecs
from datetime import datetime,timedelta
from datetime import date
import datetime

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
        self.docs=[]

        if not os.path.isdir(dirname):
            print(dirname, '- not a directory!')
            sys.exit()

        #讀取當日新聞
        for fname in self.fname:
            docs = self.read_file(self.folderName + '/' + fname, 'json')
            for i in range(len(docs)):
                #ettoday有機會爬到沒有標題的新聞
                if not docs[i]['title']:
                    docs[i]['title']='無標題'

                if not docs[i]['content']:
                    docs[i]['content']='無內文'
                self.docs.append(docs[i])

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
        
        for i in range(len(self.docs)):
            yield segment(self.docs[i]['title'])
            yield segment(self.docs[i]['content'])
        # text = open(os.path.join(self.folderName, fname),
        #             'r', encoding='utf-8', errors='ignore').read()


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
    idf_freq = documents.idf_freq
    mean_idf = documents.mean_idf
    docs=documents.docs
    i = 0
    index=0
    # freq = {}
    for doc in documents:
        i+=1
        # print(doc)
        # print(len(doc))
        # 每次讀到title欄位的時候清空freq和tfidf，標題和內文算同一篇文檔
        if i%2!=0:
            # print(i)
            freq = {}
            tfidf={}

        #計算freq
        for w in doc:
            # 如果沒有找到word，設成0，再+1。如果有找到word就+1
            freq[w] = freq.get(w, 0.0) + 1.0

        #標題
        if i%2!=0:
            pass
            # for w in doc:
            #     freq[w]*=2
            
            # pass
        #內文
        else:
            total = sum(freq.values())#文檔所有詞數量，包含標題和內文
            for k in freq:   # 計算 TF-IDF
                tfidf[k] =(freq[k]/total)*idf_freq.get(k,mean_idf)
            tags = sorted(tfidf, key=tfidf.__getitem__, reverse=True)  # 排序

            # Write TFIDF Top 10 to keywords field
            docs[index]['keywords']=[]
            for words in tags[:topK]:
                docs[index]['keywords'].append(words)
            # print('---------------------------')
            # print(docs[index])
            index+=1
            if index % 100 == 0:
                print('Documents processed: ', index, ', time: ',datetime.datetime.now())
                # return tags[:topK]


        # else:
        #     return tags
        # 寫檔
    # print('---------------------------')
    # print(docs[1])
    YTD=str(date.today()-timedelta(1))
    toList = []
    filename = 'News_'+YTD+'.json'
    DIR_NAME = "YTDnews"
    OUTPUT_DIR = os.path.join(os.path.split(os.path.realpath(__file__))[0], DIR_NAME)
    if not os.path.exists(OUTPUT_DIR):  # 先確認資料夾是否存在
        os.makedirs(OUTPUT_DIR)

    fp = codecs.open(OUTPUT_DIR + "/" + filename, "w", "utf-8")
    for i in range(len(docs)):
        # tfidf_json[i]['keywords']='daddsa'
        # print('=========================')
        # print(tfidf_json[i]['keywords'])
        docs[i]['title']=preprocess(docs[i]['title'])
        docs[i]['content']=preprocess(docs[i]['content'])
        docs[i]['description']=preprocess(docs[i]['description'])
        toList.append(docs[i])
        # print(tfidf_json[i])

    toList = json.dumps(toList, ensure_ascii=False)
    fp.write(toList)
    fp.close()
    # 讀檔
    # sentence = open(document, 'r', encoding='utf-8', errors='ignore').read()
    # tags = tdidf.extract_keywords(sentence, topK)

    # for tag in tags:
    #     print(tag)



if __name__ == "__main__":
    main(sys.argv[1:])
