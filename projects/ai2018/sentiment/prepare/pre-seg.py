#!/usr/bin/env python
#encoding=utf8
# ==============================================================================
#          \file   to_flickr_caption.py
#        \author   chenghuige  
#          \date   2016-07-11 16:29:27.084402
#   \Description   seg using dianping corpus /home/gezi/data/ai2018/sentiment/dianping/ratings.csv 
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string('seg_method', 'basic', '')
flags.DEFINE_string('name', None, '')

assert FLAGS.seg_method

import sys,os
import numpy as np

import gezi
from gezi import Segmentor 

if not gezi.env_has('BSEG') or not('pos' in FLAGS.name or 'ner' in FLAGS.name):
  segmentor = Segmentor()

#assert gezi.env_has('JIEBA_POS')
from gezi import WordCounter 

import pandas as pd

from projects.ai2018.sentiment.prepare import filter

from tqdm import tqdm
import traceback

START_WORD = '<S>'
END_WORD = '</S>'

counter = WordCounter(most_common=0, min_count=1)
counter2 = WordCounter(most_common=0, min_count=1)

print('seg_method:', FLAGS.seg_method, file=sys.stderr)

def seg(id, text, out, type):
  text = filter.filter(text)
  counter.add(START_WORD)
  counter.add(END_WORD)
  if type == 'word':
    words = segmentor.Segment(text, FLAGS.seg_method)
    for w in words:
      counter.add(w)
  else:
    l = gezi.cut(text, type)
    for x, y in l:
      counter.add(x)
      counter2.add(y)
      
    words = ['%s|%s' % (x, y) for x,y in l]
  print(id, '\x09'.join(words), sep='\t', file=out)

assert FLAGS.name
ifile = sys.argv[1]
ofile = ifile.replace('.csv', '.seg.%s.txt' % FLAGS.name)
vocab = ifile.replace('.csv', '.seg.%s.vocab' % FLAGS.name)
type_ = 'word'

vocab2 = None
if 'pos' in FLAGS.name:
  vocab2 = ifile.replace('.csv', '.pos.%s.vocab' % FLAGS.name)
  type_ = 'pos'
elif 'ner' in FLAGS.name:
  vocab2 = ifile.replace('.csv', '.ner.%s.vocab' % FLAGS.name)
  type_ = 'ner'

ids_set = set()
fm = 'w'
if os.path.exists(ofile):
  fm = 'a'
  for line in open(ofile):
    ids_set.add(line.split('\t')[0])

print('%s already done %d' % (ofile, len(ids_set)))

num_errs = 0
with open(ofile, fm) as out:
  df = pd.read_csv(ifile, lineterminator='\n')
  contents = df['content'].values 
  ids = df['id'].values
  for i in tqdm(range(len(df)), ascii=True):
    if str(ids[i]) in ids_set:
      continue
    #if i != 2333:
    #  continue
    #print(gezi.cut(filter.filter(contents[i]), type_))
    try:
      seg(ids[i], contents[i], out, type=type_)
    except Exception:
      #print(traceback.format_exc())
      num_errs += 1
      continue
    #exit(0)

counter.save(vocab)
if vocab2:
  counter2.save(vocab2)

print('num_errs:', num_errs, 'ratio:', num_errs / len(df))
