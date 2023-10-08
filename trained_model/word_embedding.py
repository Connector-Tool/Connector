#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023-04-25
@Author  : Qishuang Fu
@File    : word_embeddingg.py

"""
import json
import pandas as pd

from gensim.models import Word2Vec
from config import Config
from utils.loader import load_normalization_map


class TxWordVector:
    def __init__(self, txlist: pd.DataFrame, train=False):
        self.sample = txlist[['srcTxhash', 'function']]
        self.norm_map = load_normalization_map()
        self.train = train

    def creat_mapdict(self):
        """
            input  : self
            output: Map_Dict
        """
        map_dict={}
        for _, row in self.norm_map.iterrows():

            for raw_var in eval(row['raw_var']).values():
                if raw_var != "":
                    map_dict[raw_var] = row['norm_var']
        return map_dict

    def creat_sent(self,map_dict):
        """
            input  : self
            output: sentence,hash_sent
        """
        sentences = []
        hash_sent={}
        for _, row in self.sample.iterrows():
            func = row['function']
            hash=row['srcTxhash']
            args = func[func.index("{"):]

            args = json.loads(args)
            arg_name = [key.replace("_", "") for key in args]

            # Normalization
            arg_name = [map_dict[arg] if arg in map_dict else arg for arg in arg_name]
            arg_name = [func[:func.index("{")]] + arg_name

            sentences.append(arg_name)

            hash_sent[hash]=arg_name

        return sentences,hash_sent

    def word2vect(self, sentences, hash_sent):
        if self.train:
            model = Word2Vec(sentences, min_count=1, vector_size=1)
            model.save(Config().MODEL_DIR + "/word2vec_model.bin")
        else:
            model = Word2Vec.load(Config().MODEL_DIR + "/word2vec_model.bin")

        all_sentence_vec={}
        for hash, sentence in hash_sent.items():
        #for sentence in sentences:
            sentence_vector = []
            for word in sentence:
                sentence_vector.append(model.wv[word] if word in model.wv else [0]*model.vector_size)

            all_sentence_vec[hash]=sentence_vector

        return all_sentence_vec

    def wordembedd(self):

        map_dict = self.creat_mapdict()

        sentences, hash_sent = self.creat_sent(map_dict)

        all_sentence_vec = self.word2vect(sentences, hash_sent)

        return all_sentence_vec





