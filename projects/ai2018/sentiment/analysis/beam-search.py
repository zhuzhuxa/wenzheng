#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# ==============================================================================
#          \file   beam-search.py
#        \author   chenghuige  
#          \date   2018-10-24 15:27:26.697918
#   \Description  
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys 
import os

import gezi
  
import pandas as pd  
import numpy as np

import beam_f

ATTRIBUTES = ['location_traffic_convenience', 'location_distance_from_business_district', 'location_easy_to_find',
              'service_wait_time', 'service_waiters_attitude', 'service_parking_convenience', 'service_serving_speed', 
              'price_level', 'price_cost_effective', 'price_discount', 
              'environment_decoration', 'environment_noise', 'environment_space', 'environment_cleaness',
              'dish_portion', 'dish_taste', 'dish_look', 'dish_recommendation',
              'others_overall_experience', 'others_willing_to_consume_again']

CLASSES = ['na', 'neg', 'neu', 'pos']

num_attrs = len(ATTRIBUTES)
NUM_ATTRIBUTES = num_attrs
num_classes = 4
NUM_CLASSES = num_classes
N = NUM_CLASSES
idx = 2

infile = sys.argv[1] if len(sys.argv) > 1 else './mount/temp/ai2018/sentiment/submit6/word.glove_rnet.3layer_model.ckpt-13.00-42666.valid.csv'
df = pd.read_csv(infile)
scores = df['score'].values

scores = df['score']
scores = [gezi.str2scores(score) for score in scores] 
scores = np.array(scores)
scores = np.reshape(scores, [-1, NUM_ATTRIBUTES, NUM_CLASSES])
probs = gezi.softmax(scores)

labels = df.iloc[:,idx:idx+num_attrs].values
predicts = df.iloc[:,idx+num_attrs:idx+2*num_attrs].values

index = 1
scores = scores[:, index, :]
labels = labels[:, index]
probs = probs[:, index, :]
probs = np.reshape(probs, [NUM_CLASSES, -1])

bi_concave_iters = 1000
conf_opt_iters = 5

weights = np.load('./mount/temp/ai2018/sentiment/class_weights.npy')
weights = weights[index]

#weights = [1.] * len(CLASSES)
#weights = np.array(weights)
y = labels + 2
eps = 2.
reg = 3.
thresh = 0.1

print(y.shape)
print(probs.shape)

result = beam_f.seed_beam_f(N, 
                            weights, 
                            y,
                            bi_concave_iters, 
                            conf_opt_iters,
                            probs,
                            eps, 
                            reg, 
                            thresh, 
                            last_k=100,
                            out_put=None, 
                            restarts=5)

print(result)