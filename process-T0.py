#!/usr/bin/env python
# coding: utf-8

import json
import os
import regex as re

t0root = "/Users/yvon/dat/Projects/2021-BigScience/evaluation-results/t0/bigsciencelmevalharness/transformers/all/"
t0file = "examples-bigscience-T0_wmt14_fr_en_0_1234_2022-07-01T11:42:20.160142.jsonl"
t0path = t0root + t0file

# examples.model=opt.task=wmt14_fr_en.templates=xglm-fr-en-source+target.fewshot=0.seed=1234.timestamp=2023-01-11T22_31_48.jsonl
model = "t0"
seed  = "1234"
task  = "wm14_fr_en"
templates = None
fewshot = None
tstamp = "2022-07-01T11:42:20"
nsamples = 0
newroot = "/Users/yvon/dat/Projects/2021-BigScience/mt-bigscience/outputs/wmt14_fr_en/0-shot/jsonl/"
name = newroot + "examples.model=" + model
name = name + ".task=" + task
name = name + ".templates=TEMPLATE"
name = name + ".fewshot=FEWSHOT"
name = name + ".seed=" + seed
name = name + ".timestamp=" + tstamp
name = name + ".jsonl"

with open(path, "r") as fp:
    print(type(raw))
    print(list(raw))
    for line in (fp):
        raw = json.loads(line)
        if (templates != raw["prompt_name"] or fewshot != raw["fewshot_num"]):
            if (nsamples > 0):
                print("*** printed:", nsamples) 
            fewshot   = raw["fewshot_num"]
            templates = raw["prompt_name"]
            file = re.sub("FEWSHOT", str(fewshot), name)
            file = re.sub("TEMPLATE", templates, file)
            print("*** newfile:", file)
            op = open(file, "w")
            nsamples = 0
        nsamples = nsamples + 1
        print(line, file = op, end="")
        


# In[ ]:





# In[ ]:




