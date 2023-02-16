#!/usr/bin/env python
# coding: utf-8

# In[259]:


import pandas as pd
import numpy as np
import regex as re
import math
import os


# In[365]:


# Parse the template to extract: 
# - the instruction /prompt, 
# - the source
# - the target
# - the type (only target, or source and target)
# also returns a "normalized" version of the prompt
def parse_wmt_template(template):
    # print(template)
    if (template == "gpt3-fr-en" or template == "gpt3-en-fr"):
        template = template + "-target"
    template = re.sub("gpt\-3", "gpt3", template)
    template = re.sub("translate\_as\_", "translate_as-", template)
    template = re.sub("source\-target", "source+target", template)
    [prompt, src, trg, prptype] = template.split("-")
    
    template = re.sub("gpt3", "gpt-3", template)
    prompt   = re.sub("gpt3", "gpt-3", prompt)   
    return([prompt, src, trg, prptype, template])

print(parse_wmt_template("gpt-3-en-fr-source+target"))


# In[277]:


# normalize post processing procedure, adding 'none' when none is used
def parse_wmt_postproc(postproc):
    p = re.sub('^[0-9]+\.?', '', str(postproc))
    if (p == "" or p == "nan" or p == "NaN"):
        p = "none"
    return(p)

# normalize model names
def parse_wmt_model(model):
    if (model == "bloom-6b3"):
        model = "bloom-7b1"
    return(model)


# In[333]:


from pathlib import Path 
def collect_results(path=None, task = "*", metric = "bleu", shot="*"):
    """
    Collect results from all datasets as csv files
    """
    dfslst = []
    root_dir = Path(path)
    # files = source_dir.iterdir()
    pattern = task + "/" + shot + "/" + "*" + metric + "*.tsv"
    # print(pattern)
    files = root_dir.glob(pattern)
    # files = root_dir.glob('*/*/*bleu*.tsv')
    print(files)
    for file in files:
        # print(file.name)       
        dfslst.append(pd.read_csv(file, 
                                  sep="\t", 
                                  header=0, 
                                  dtype = {'model':str,'task':str,'template':str,'fewshot':int,'seed':int,'postproc':str,'timestamp':str,'filename':str,'spBLEU':float},
                                  index_col=False))   
    allres = pd.concat(dfslst)
    # print(allres['template'])
    post = allres['postproc'].apply(parse_wmt_postproc)
    allres['postproc'] = post
    prompt = allres['template'].apply(parse_wmt_template)
    # newdf = pd.DataFrame([c[0] for c in xa], [c[1] for c in xa], [c[2] for c in xa],[c[3] for c in xa])
    # newdf = pd.DataFrame({"name":[c[0] for c in xa],"src":[c[1] for c in xa], "trg":[c[2] for c in xa], "type":[c[3] for c in xa]})
    for (cname, cindex) in [("prompt", 0), ("src", 1), ("trg", 2), ("prptype", 3), ("template", 4)]:
        allres[cname] = [c[cindex] for c in prompt.values]
    return(allres)
    # df.assign(newdf)

rootdir  = "/Users/yvon/dat/Projects/2021-BigScience/mt-bigscience/outputs/"
allres   = collect_results(rootdir, task="wmt14*", metric="bleu")

# allcomet = collect_results(rootdir, task="wmt14*", metric="comet")
# print(allres.head)
print(allres.shape)
allres.to_csv("/Users/yvon/Downloads/allres.csv")


# ## Main table ##
# The first table is about getting all the results we have for one prompt (xglm source target), all languages pairs, in two versions. The models considered are:
# - bloom
# - t0
# - opt
# - T0pp

# In[334]:


mask = pd.array(allres['prompt'] == "xglm",dtype="boolean") & \
    pd.array(allres['fewshot'] < 2, dtype="boolean") & \
    pd.array(allres['postproc'] != "newline-cut") &\
    (pd.array(allres['model'] == "bloom",dtype="boolean") |
     pd.array(allres['model'] == "t0",dtype="boolean") |
     pd.array(allres['model'] == "opt", dtype="boolean")) &\
    pd.array(allres['prptype'] == "source+target")
filtered = allres[mask]
selected = filtered.loc[:, ['model', 'fewshot', 'postproc', 'spBLEU', 'src', 'trg',]]
selected.drop_duplicates(keep='first', inplace=True, ignore_index=True)
print(selected.sort_values(by=['fewshot', 'src', 'trg', 'model', 'postproc'], axis=0))


# ----
# ### Analysis of languages occurring in the output translations ###
# This analysis relies on fast text, and is based on the same configurations as for the previous table: 
# one prompt, all language pairs
# ----

# In[361]:


import fasttext
lid_model = fasttext.load_model('Analysis/Outputs/lid.176.ftz')

def detector(text):
    text = str(text)
    # return empty string if there is no tweet
    if text.isspace():
        return ""
    else:
        # get first item of the prediction tuple, then split by "__label__" and return only language code
        text = re.sub("\n", " ", text)
        return lid_model.predict(text)[0][0].split("__label__")[1]

def perlang_analysis(models, postprocs):
    mask = pd.array(allres['prompt'] == "gpt-3", dtype="boolean") & \
    pd.array(allres['fewshot'] < 2, dtype="boolean") & \
    pd.array(allres['postproc'].isin(postprocs)) &\
    pd.array(allres['model'].isin(models)) &\
    pd.array(allres['prptype'] == "target")
    filtered = allres[mask]
    selected = filtered.loc[:, ['task', 'fewshot', 'filename', 'src', 'trg']]

    selected['path'] = rootdir + selected['task'] + "/" + selected['fewshot'].astype(str) + "-shot/tsv/" + selected['filename']
    L = selected.loc[:,'path'].to_list()
    L.sort()
    for wmtoutput in L:
    
        print('\n**** wmt output:', wmtoutput, '\n')
        # Make sure quoting = 3 - this matters to avoid errors
        translations = pd.read_csv(wmtoutput, sep='\t', quoting=3, engine = "python", on_bad_lines='warn', names = ['ctx','ref','hyp'], dtype={0:str, 1:str, 2:str})
        # print(translations.shape)
        # print(translations.head())
    
        translations['empty'] = translations.apply(lambda row: len(str(row.hyp)) == 0, axis=1)
        translations['ldiff'] = translations.apply(lambda row: len(str(row.ref)) - len(str(row.hyp)),axis=1)
        translations['lang'] = translations.apply(lambda row: detector(row.hyp), axis=1)
        print(translations.groupby('lang').describe())
        print(translations.groupby('empty').describe()) 

models = ["bloom"]
postprocs = ["newline-cut-custom-truncate"]
perlang_analysis(models, postprocs)


# ### Third table, Number of shots ###
# bloom xglm prompt, all directions and pairs, show the effect of increasing the fewshot = 0-5
# 

# In[336]:


def pershot_analysis():
    mask = pd.array(allres['prompt'] == "xglm", dtype="boolean") & \
    pd.array(allres['fewshot'] < 6 , dtype="boolean") & \
    pd.array(allres['postproc'] != "newline-cut") &\
    pd.array(allres['model'] == "bloom", dtype="boolean") &\
    pd.array(allres['prptype'] == "source+target")
    filtered = allres[mask]
    selected = filtered.loc[:, ['model', 'fewshot', 'postproc', 'spBLEU', 'src', 'trg',]]
    selected.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    print(selected.sort_values(by=['model', 'src', 'trg', 'postproc', 'fewshot'], axis=0))

pershot_analysis()


# ### Show variability by prompt ### 
# This analysis is run for all models, with a restricted list of prompts.

# In[432]:


def permodel_analysis(allres, metric="spBLEU", metriclab = "BLEU"):
    modelList = [
    "bloom-560m", 
    "bloom", 
    "bloom-1b1", 
#    "bloom-1b7", 
    "bloom-3b", 
    "bloom-7b1"
    ]
    templateList = [
    "a_good_translation-en-fr-source+target", "a_good_translation-en-fr-target", \
    "a_good_translation-fr-en-source+target", "a_good_translation-fr-en-target", \
    "gpt3-en-fr-target", "gpt3-fr-en-target", \
    "translate_as-en-fr-target", "translate_as-fr-en-target", \
    "version-en-fr-target", "version-fr-en-target", \
    "xglm-en-fr-source+target", "xglm-en-fr-target", \
    "xglm-fr-en-source+target", "xglm-fr-en-target",
    "a_good_translation-en-hi-source+target", "a_good_translation-en-hi-target", \
    "a_good_translation-hi-en-source+target", "a_good_translation-hi-en-target", \
    "gpt3-en-hi-target", "gpt3-hi-en-target", \
    "translate_as-en-hi-target", "translate_as-hi-en-target", \
    "version-en-hi-target", "version-hi-en-target", \
    "xglm-en-hi-source+target", "xglm-en-hi-target", \
    "xglm-hi-en-source+target", "xglm-hi-en-target",
    ] 

    mask = pd.array(allres['fewshot'] < 2 , dtype="boolean") & \
    pd.array(allres['postproc'] != "newline-cut") & \
    pd.array(allres['model'].isin(modelList)) & \
    pd.array(allres['template'].isin(templateList))

    filtered = allres[mask]
    selected = filtered.loc[:, ['model', 'fewshot', 'postproc', metric, 'src', 'trg', 'prompt', 'prptype']]
    selected.drop_duplicates(keep='first', inplace=True, ignore_index=True)
    alltab = []

    hien = [('en', 'hi'), ('hi', 'en')]
    fren = [('en', 'fr'), ('fr', 'en')]
    for postproc in ["none", "newline-cut-custom-truncate"]:
        for langpairs in hien, fren:
            alllst = []
            keylst = []
            for shot in [0,1]:
                for (src, trg) in langpairs:    
                # print(sel.head())
                    mask = pd.array(selected['src'] == src, dtype="boolean") & pd.array(selected['trg'] == trg, dtype="boolean")
                    sel = selected[mask]
                    sel = sel[sel['fewshot'] == shot] # .loc[:,['model_name','score']]
                    sel = sel[sel['postproc'] == postproc] # .loc[:,['model_name','score']]
                    filt = sel.loc[:,['model','spBLEU']]
                    # print(sel.head())
                    # print("\n**** Source / target", src, trg, " **** shots", shot, "**** postproc", postproc, "****")
                    tab = filt.groupby(['model']).describe(percentiles=[])
                    alllst.append(tab)
                    keylst.append(src + "-" + trg + " (" + str(shot) + "-shot)")
                    # 
                    if (tab.shape[0] > 10):
                        print(tab.to_latex(
                        #header = ['avg', 'min' , 'max'],
                        columns = [(metric, 'mean'), (metric, 'min'), (metric, 'max')],
                        float_format = "%.2f",
                        caption = metriclab + " by model for " + src + "-" + trg + " (" + str(shot) + " shot, " + postproc + ")"
                        ))
            alltab = pd.concat(alllst, axis = 1, keys = keylst)
            # print(alltab)
            print("\n**** Source / target", src, trg, "**** postproc", postproc, " ****")
            if (alltab.shape[0] > 0):
                cols = [(key, metric, heading) for (key, heading) in [(k, h) for k in keylst for h in ['mean','min', 'max']]]
                print(alltab.to_latex(
                        #header = ['avg', 'min' , 'max'],
                        columns = cols,
                        multicolumn = True,
                        float_format = "%.2f",
                        caption = metriclab + " by model for " + src + "-" + trg + " (" + postproc + ")"
                        ))
    return(1)
                      
permodel_analysis(allres, metric="spBLEU", metriclab = "BLEU scores") 


# In[433]:


# Like previous function, could be improved by dropping one level of indexing
def perprompt_analysis(allres, metric="spBLEU", metriclab = "BLEU"):
    modelList = [
    "bloom-560m", 
    "bloom", 
    "bloom-1b1", 
#    "bloom-1b7", 
    "bloom-3b", 
    "bloom-7b1"
    ]
    templateList = [
    "a_good_translation-en-fr-source+target", "a_good_translation-en-fr-target", \
    "a_good_translation-fr-en-source+target", "a_good_translation-fr-en-target", \
    "gpt3-en-fr-target", "gpt3-fr-en-target", \
    "translate_as-en-fr-target", "translate_as-fr-en-target", \
    "version-en-fr-target", "version-fr-en-target", \
    "xglm-en-fr-source+target", "xglm-en-fr-target", \
    "xglm-fr-en-source+target", "xglm-fr-en-target",
    "a_good_translation-en-hi-source+target", "a_good_translation-en-hi-target", \
    "a_good_translation-hi-en-source+target", "a_good_translation-hi-en-target", \
    "gpt3-en-hi-target", "gpt3-hi-en-target", \
    "translate_as-en-hi-target", "translate_as-hi-en-target", \
    "version-en-hi-target", "version-hi-en-target", \
    "xglm-en-hi-source+target", "xglm-en-hi-target", \
    "xglm-hi-en-source+target", "xglm-hi-en-target",
    ] 

    mask = pd.array(allres['fewshot'] < 2 , dtype="boolean") & \
    pd.array(allres['postproc'] != "newline-cut") & \
    pd.array(allres['model'].isin(modelList)) & \
    pd.array(allres['template'].isin(templateList))

    filtered = allres[mask]
    selected = filtered.loc[:, ['model', 'fewshot', 'postproc', 'spBLEU', 'src', 'trg', 'prompt', 'prptype']]
    selected.drop_duplicates(keep='first', inplace=True, ignore_index=True)

    hien = [('en', 'hi'), ('hi', 'en')]
    fren = [('en', 'fr'), ('fr', 'en')]
    for postproc in ["none", "newline-cut-custom-truncate"]:
        for langpairs in hien, fren:
            alllst = []
            keylst = []
            for shot in [0,1]:
                for (src, trg) in langpairs:    
                # print(sel.head())
                    mask = pd.array(selected['src'] == src, dtype="boolean") & pd.array(selected['trg'] == trg, dtype="boolean")
                    sel = selected[mask]
                    sel = sel[sel['fewshot'] == shot] # .loc[:,['model_name','score']]
                    sel = sel[sel['postproc'] == postproc] # .loc[:,['model_name','score']]
                    filt = sel.loc[:,['prompt', 'prptype', 'spBLEU']]
                    # print(sel.head())
                    # print("\n**** Source / target", src, trg, " **** shots", shot, "**** postproc", postproc, "****")
                    tab = filt.groupby(['prompt', 'prptype']).describe(percentiles=[])
                    alllst.append(tab)
                    keylst.append(src + "-" + trg + " (" + str(shot) + "-shot)")
                    # print(tab)
                    #print(tab.to_latex(
                    # header = ['avg', 'min' , 'max'],
                    #    columns = [(metric, 'mean'), (metric, 'min'), (metric, 'max')],
                    #   float_format = "%.2f",
                    #   caption = metriclab + " by prompt for " + src + "-" + trg + " (" + str(shot) + " shot, " + postproc + ")"
                    #))
            alltab = pd.concat(alllst, axis = 1, keys = keylst)
            # print(alltab)
            print("\n**** Source / target", src, trg, "**** postproc", postproc, " ****")
            if (alltab.shape[0] > 0):
                cols = [(key, metric, heading) for (key, heading) in [(k, h) for k in keylst for h in ['mean','min', 'max']]]
                print(alltab.to_latex(
                        #header = ['avg', 'min' , 'max'],
                        columns = cols,
                        multicolumn = True,
                        float_format = "%.2f",
                        caption = metriclab + " per prompt for " + src + "-" + trg + " (" + postproc + ")"
                        ))
    return(1)

perprompt_analysis(allres, metric="spBLEU", metriclab = "BLEU scores") 

