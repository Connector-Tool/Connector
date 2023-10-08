#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   classifier.py
@Time    :   2023/04/25 10:24:40
@Author  :   zzYe, Qishuang Fu
'''

import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 上两级目录的路径
parent_path = os.path.dirname(os.path.dirname(script_path))
# 根目录的路径
root_path = os.path.abspath(parent_path)

import sys
sys.path.append(root_path)

import joblib
import numpy as np
import pandas as pd

from random import randint
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from config import Config
from trained_model.word_embedding import TxWordVector
from trained_model.structure_embedding import TxStructureVector


def load_data(raw_tx, label):
    # Define embedding size
    STRUCTURE_EMBED_SIZE = 16
    SENTENCE_EMBED_SIZE = 36

    print("Load data ...")

    # Get hash label
    label_map = dict()
    df = label[['srcTxhash', 'label']]

    for _, row in df.iterrows():
        label_map[row['srcTxhash']] = row['label']

    # Get sturcture vectors
    structure_vecs = TxStructureVector(
        raw_tx=raw_tx
    ).count_motif()

    # Get sentences vectors
    sentence_vecs = TxWordVector(
        txlist=label,
        train=True
    ).wordembedd()

    # Create feature
    feature, label = [], []
    for key, val in structure_vecs.items():
        if key not in label_map:
            continue
        structure_feat = [val[i] if i in val else 0.0 for i in range(STRUCTURE_EMBED_SIZE)]
        sentence_feat = [i for arr in sentence_vecs[key] for i in arr]
        sentence_feat = sentence_feat + [0.0 for _ in range(SENTENCE_EMBED_SIZE - len(sentence_feat))]

        feature.append(structure_feat + sentence_feat)
        label.append(label_map[key])
    return np.array(feature), np.array(label)


def add_result(r, metric, classifier, value):
    if classifier in r[metric]:
        r[metric][classifier] += value
    else:
        r[metric][classifier] = value
    return r


def train_model(feature, label):
    classifiers = [
        RandomForestClassifier(n_jobs=10),
    ]
    POS_LABEL = 1

    r = {'acc': {}, 'pre': {}, 'rec': {}, 'f1': {}, 'auc': {}}

    splits = 1

    X_train, X_test, y_train, y_test = train_test_split(feature, label, test_size=0.8, random_state=42)

    y_train = y_train.ravel()
    y_test = y_test.ravel()

    for clf in classifiers:
        name = clf.__class__.__name__
        clf.fit(X_train, y_train)
        joblib.dump(clf, Config().MODEL_DIR + "/model.pkl")
        train_predictions = clf.predict(X_test)
        acc = accuracy_score(y_test, train_predictions)
        pre = precision_score(y_test, train_predictions, average='binary', pos_label=POS_LABEL)
        rec = recall_score(y_test, train_predictions, average='binary', pos_label=POS_LABEL)
        f1 = f1_score(y_test, train_predictions, average='binary', pos_label=POS_LABEL)
        auc = roc_auc_score(y_test, train_predictions)

        r = add_result(r, 'acc', name, acc)
        r = add_result(r, 'pre', name, pre)
        r = add_result(r, 'rec', name, rec)
        r = add_result(r, 'f1', name, f1)
        r = add_result(r, 'auc', name, auc)

        importance = clf.feature_importances_
        for i, v in enumerate(importance):
            print('Feature: %0d, Score: %.5f' % (i, v))

    for metric in r.keys():
        for clf in r[metric].keys():
            r[metric][clf] = r[metric][clf] / float(splits)

    print('\nmethod ', end='')
    [print("{:6}".format(clf), end=' ') for clf in r['pre'].keys()]
    for metric in r.keys():
        print('\n{:3}'.format(metric), end=' ')
        for clf in r[metric].keys():
            print("{0:.4f}".format(r[metric][clf]), end=' ')


if __name__ == '__main__':
    feature, label = load_data()
    train_model(feature, label)



