# -*- coding: UTF-8 -*-
#   Copyright (c) 2019 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import os
import time
import sys

import paddle.fluid as fluid
import paddle

import jieba.lac_small.utils as utils  # 工具类
import jieba.lac_small.creator as creator
import jieba.lac_small.reader_small as reader_small
import numpy

word_emb_dim=128
grnn_hidden_dim=128
bigru_num=2
use_cuda=False
basepath = os.path.abspath(__file__)
folder = os.path.dirname(basepath)
init_checkpoint = os.path.join(folder, "model_baseline")
batch_size=1

dataset = reader_small.Dataset()  # Dataset对象，处理原始输入
infer_program = fluid.Program()
with fluid.program_guard(infer_program, fluid.default_startup_program()):
    with fluid.unique_name.guard():
        infer_ret = creator.create_model(dataset.vocab_size, dataset.num_labels, mode='infer')  # 模型创建器creator
infer_program = infer_program.clone(for_test=True)
place = fluid.CPUPlace()
exe = fluid.Executor(place)
exe.run(fluid.default_startup_program())
utils.init_checkpoint(exe, init_checkpoint, infer_program)
results = []

def get_sent(str1):
    """深度学习序列标注分词"""
    feed_data=dataset.get_vars(str1)
    a = numpy.array(feed_data).astype(numpy.int64)
    a=a.reshape(-1,1)
    c = fluid.create_lod_tensor(a, [[a.shape[0]]], place)

    words, crf_decode = exe.run(
            infer_program,
            fetch_list=[infer_ret['words'], infer_ret['crf_decode']],
            feed={"words":c, },
            return_numpy=False,
            use_program_cache=True)
    sents=[]
    sent,tag = utils.parse_result(words, crf_decode, dataset)
    sents = sents + sent
    return sents

def get_result(str1):
    """深度学习 分词+词性标注"""
    feed_data=dataset.get_vars(str1)
    a = numpy.array(feed_data).astype(numpy.int64)
    a=a.reshape(-1,1)
    c = fluid.create_lod_tensor(a, [[a.shape[0]]], place)

    words, crf_decode = exe.run(
            infer_program,
            fetch_list=[infer_ret['words'], infer_ret['crf_decode']],
            feed={"words":c, },
            return_numpy=False,
            use_program_cache=True)
    results=[]
    results += utils.parse_result(words, crf_decode, dataset)
    return results