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

# In[329]:


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
    "xglm-fr-en-source+target", "xglm-fr-en-target"] 


    mask = pd.array(allres['fewshot'] < 2 , dtype="boolean") & \
    pd.array(allres['postproc'] != "newline-cut") & \
    pd.array(allres['model'].isin(modelList)) & \
    pd.array(allres['template'].isin(templateList))

    filtered = allres[mask]
    selected = filtered.loc[:, ['model', 'fewshot', 'postproc', 'spBLEU', 'src', 'trg', 'prompt', 'prptype']]
    selected.drop_duplicates(keep='first', inplace=True, ignore_index=True)


    for (src, trg) in [('en','fr'), ('fr', 'en'), ('en', 'hi'), ('hi', 'en')]:
        for postproc in ["none", "newline-cut-custom-truncate"]:
            for shot in [0,1]:
                # print(sel.head())
                mask = pd.array(selected['src'] == src, dtype="boolean") & pd.array(selected['trg'] == trg, dtype="boolean")
                sel = selected[mask]
                sel = sel[sel['fewshot'] == shot] # .loc[:,['model_name','score']]
                sel = sel[sel['postproc'] == postproc] # .loc[:,['model_name','score']]
                filt = sel.loc[:,['model','spBLEU']]
                # print(sel.head())
                print("\n**** Source / target", src, trg, " **** shots", shot, "**** postproc", postproc, "****")
                tab = filt.groupby(['model']).describe(percentiles=[])
                print(tab)
                print(tab.to_latex(
                    # header = ['avg', 'min' , 'max'],
                    columns = [('spBLEU', 'mean'), ('spBLEU', 'min'), ('spBLEU', 'max')],
                   float_format = "%.2f",
                   caption = metriclab + " by model for " + src + "-" + trg + " (" + str(shot) + " shot, " + postproc + ")"
                ))

permodel_analysis(allres,metric="spBLEU", metriclab = "BLEU scores") 


# In[356]:


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


    for (src, trg) in [('en','fr'), ('fr', 'en'), ('en', 'hi'), ('hi', 'en')]:
        for postproc in ["none", "newline-cut-custom-truncate"]:
            for shot in [0,1]:
                # print(sel.head())
                mask = pd.array(selected['src'] == src, dtype="boolean") & pd.array(selected['trg'] == trg, dtype="boolean")
                sel = selected[mask]
                sel = sel[sel['fewshot'] == shot] # .loc[:,['model_name','score']]
                sel = sel[sel['postproc'] == postproc] # .loc[:,['model_name','score']]
                filt = sel.loc[:,['prompt', 'prptype', 'spBLEU']]
                # print(sel.head())
                print("\n**** Source / target", src, trg, " **** shots", shot, "**** postproc", postproc, "****")
                tab = filt.groupby(['prompt', 'prptype']).describe(percentiles=[])
                print(tab)
                print(tab.to_latex(
                    # header = ['avg', 'min' , 'max'],
                    columns = [('spBLEU', 'mean'), ('spBLEU', 'min'), ('spBLEU', 'max')],
                   float_format = "%.2f",
                   caption = metriclab + " by prompt for " + src + "-" + trg + " (" + str(shot) + " shot, " + postproc + ")"
                ))

perprompt_analysis(allres,metric="spBLEU", metriclab = "BLEU scores") 


# # Below is older stuff, yet useful code

# In[3]:


task = "Analysis/wmt14_hi_en"
taskfile = task + ".csv"
print(taskfile)

if (not os.access(taskfile, os.F_OK)):
    # collect_results(task)
    print("no datafile")
    
df = pd.read_csv(taskfile)

if re.match("Analysis/wmt14_hi_en", task):
    x = df["prompt_name"].apply(parse_wmt_prompt)
    xa = x.values
    print(xa[0])
    # newdf = pd.DataFrame([c[0] for c in xa], [c[1] for c in xa], [c[2] for c in xa],[c[3] for c in xa])
    # newdf = pd.DataFrame({"name":[c[0] for c in xa],"src":[c[1] for c in xa], "trg":[c[2] for c in xa], "type":[c[3] for c in xa]})
    for (cname, cindex) in [("name",0), ("src",1), ("trg",2), ("type",3)]:
        df[cname] = [c[cindex] for c in xa]
    
    # df.assign(newdf)
    
df.head()    
# df.head()


# In[5]:


# selection
# columns 
df.loc[:,'score':'type']
df.loc[:,['model_name','score','fewshots','src','trg','name','type']]
print(df.loc[:,'score'].count())
# df.loc[:,'score'].mean()
# print(df.loc[:,'score'].min())

# Analysis by model
for src in ['en','hi']:
    for shot in [0,1]:
        sel = df.loc[:,['model_name','score','fewshots','src']]
        # print(sel.head())
        sel = sel[sel['src'] == src]
        sel = sel[sel['fewshots'] == shot] # .loc[:,['model_name','score']]
        resel = sel.loc[:,['model_name','score']]
        # print(sel.head())
        print("\n**** Source", src, " **** shots", shot, "****")
        print(resel.groupby('model_name').describe(percentiles=[.5]))


# In[7]:


# Analysis by prompt
for src in ['en','hi']:
    for shot in [0,1]:
        sel = df.loc[:,['name','score','fewshots','src']]
        # print(sel.head())
        sel = sel[sel['src'] == src]
        sel = sel[sel['fewshots'] == shot] # .loc[:,['model_name','score']]
        resel = sel.loc[:,['name','score']]
        # print(sel.head())
        print("\n**** Source", src, " **** shots", shot, "****")
        print(resel.groupby('name').describe(percentiles=[0.5]))


# Analyse typique d'un fichier tsv pour voir ce qu'ils ont dans le ventre
# On s'intéresse surtout aux questions de longueur et aux questions de langue
# 
# TODO: rewrite this piece of code with correct file names from the dataset

# In[191]:


# wmtoutput = 'Analysis/Outputs/bloom176b/examples.model=bloom.task=wmt14_fr_en.templates=version-en-fr-target.fewshot=1.batchsize=4.seed=1234.timestamp=2022-09-09T09-10-25.tsv'
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

for wmtoutput in [
    # 'Analysis/Outputs/bloom176b/en-fr-0.csv','Analysis/Outputs/bloom176b/en-fr-1.csv' 
    'Analysis/Outputs/bloom176b/examples--gpfsscratch-rech-six-commun-uan68tv-model-conversion-bloom_wmt14_fr_en_version-en-fr-target_0_1234_2022-08-15T22-15-12.997620.tsv',
    'Analysis/Outputs/bloom176b/examples--gpfsscratch-rech-six-commun-uan68tv-model-conversion-bloom_wmt14_fr_en_version-fr-en-target_0_1234_2022-08-15T22-15-12.997178.tsv',
    'Analysis/Outputs/bloom176b/examples--gpfsscratch-rech-six-commun-uan68tv-model-conversion-bloom_wmt14_fr_en_xglm-en-fr-target_0_1234_2022-08-15T22-15-12.997762.tsv',
    'Analysis/Outputs/bloom176b/examples--gpfsscratch-rech-six-commun-uan68tv-model-conversion-bloom_wmt14_fr_en_xglm-fr-en-target_0_1234_2022-08-15T22-15-12.998130.tsv',
    'Analysis/Outputs/bloom176b/examples.model=bloom.task=wmt14_fr_en.templates=version-en-fr-target.fewshot=1.batchsize=4.seed=1234.timestamp=2022-09-09T09-10-25.tsv',
    'Analysis/Outputs/bloom176b/examples.model=bloom.task=wmt14_fr_en.templates=version-fr-en-target.fewshot=1.batchsize=4.seed=1234.timestamp=2022-09-09T14-13-13.tsv',
    'Analysis/Outputs/bloom176b/examples.model=-gpfsscratch-rech-six-commun-uan68tv-model-conversion-bloom.task=wmt14_fr_en.templates=translate-fr-en-source+target.fewshot=1.batchsize=4.seed=1234.timestamp=2022-09-20T19-11-40.tsv'
    ]:
    
    print('\n**** wmt output:', wmtoutput, '\n')

    translations = pd.read_csv(wmtoutput, sep='\t', on_bad_lines='warn', names = ['ctx','ref','hyp'], dtype={0:str, 1:str, 2:str})
    # print(translations.shape)
    # print(translations.head())
    
    translations['empty'] = translations.apply(lambda row: len(str(row.hyp)) == 0, axis=1)
    translations['ldiff'] = translations.apply(lambda row: len(str(row.ref)) - len(str(row.hyp)),axis=1)
    translations['lang'] = translations.apply(lambda row: detector(row.hyp), axis=1)
    print(translations.groupby('lang').describe())
    print(translations.groupby('empty').describe())
    


# In the next part, we study the output of various models wrt the "language model" task. The corpus creation effort is document in https://openreview.net/pdf?id=UoEw6KigkUn.
# The question we study are:
# - how does bloom compare with alternative pLMs, monolingual and bilingual
# - which languages are easy to model with Bloom ?
# And try to see the difference between being, or not being, a bloom language.
# 
# Resuls so far are *very* weird - hard to analyze, because Vietnamese, Russian and Urdu have a very small ppl
# PPL is computed here : https://github.com/bigscience-workshop/lm-evaluation-harness/blob/ef135e98e7320f322333cd0e378dba1e95eee807/lm_eval/api/metric.py#L134
# 

# In[10]:


task = "Analysis/gsarti"
taskfile = task + ".csv"
print(taskfile)

def task2lang(task:str):
    return re.sub("gsarti/flores_101_","",task)

if (not os.access(taskfile, os.F_OK)):
    # collect_results(task)
    print("no datafile")
    
df = pd.read_csv(taskfile, index_col=0)
df.drop_duplicates(keep='first', inplace=True, ignore_index=True)
# df
df["lang"] = df["task_name"].apply(task2lang)
print(df.shape)
df.head()


# In[11]:


# An analysis by language
for task in ['gsarti/flores_101_eng','gsarti/flores_101_fra', 'gsarti/flores_101_spa','gsarti/flores_101_zho_trad','gsarti/flores_101_ara','gsarti/flores_101_por','gsarti/flores_101_vie','gsarti/flores_101_ind','gsarti/flores_101_cat','gsarti/flores_101_hin','gsarti/flores_101_ben','gsarti/flores_101_yor','gsarti/flores_101_wol']:
    sel = df.loc[:,['model_name','task_name','metric','score']]
    # print(sel.head())
    sel = sel[(sel['task_name'] == task) & (sel['metric'] == 'byte_perplexity')]
    sel.drop_duplicates(inplace=True, ignore_index=True)
    print("\n**** Task", task, "****")
    print(sel.sort_values(by='score', axis=0))
    # stats = sel.groupby('model_name').describe(percentiles=[])
    # print(stats.sort_values(by='mean', axis=0))

# Languages not in BLOOM
for task in ['gsarti/flores_101_ron', 'gsarti/flores_101_dan','gsarti/flores_101_deu','gsarti/flores_101_rus','gsarti/flores_101_slk','gsarti/flores_101_jpn']:
    sel = df.loc[:,['model_name','task_name','metric','score']]
    # print(sel.head())
    sel = sel[(sel['task_name'] == task) & (sel['metric'] == 'byte_perplexity')]
    print("\n**** Task", task, "****")
    sel.drop_duplicates(inplace=True, ignore_index=True)
    print(sel.sort_values(by='score', axis=0))
    # print(sel.groupby('name').describe(percentiles=[0.5]))


# In[12]:


# An analysis by model
print(df.shape)
for model in ['bloom176b','opt175b', 'mgpt', 'gpt-j']:
    sel = df.loc[:,['model_name','task_name','metric','score']]
    # print(sel.head())
    sel = sel[(sel['model_name'] == model) & (sel['metric'] == 'byte_perplexity')]
    print(sel.head())
    print(sel.shape)

sel = df.loc[:,['model_name','task_name','metric','score']]
sel = sel[sel['metric'] == 'byte_perplexity']
sel.drop_duplicates(inplace=True,ignore_index=True)
lang = sel.pivot(index='task_name', columns='model_name', values='score').sort_values(by='bloom176b',axis=0)
print(lang.sort_values(by='bloom176b',axis=0))


# In[13]:


# try to plot the series
import numpy as np
import regex as re
import matplotlib.pyplot as plt

langcode = [re.sub("gsarti/flores_101_","", l) for l in lang.index.array]
bloom176 = lang['bloom176b'].array
opt175 = lang['opt175b'].array
mgpt = lang['mgpt'].array

plt.figure(figsize=(12, 5), dpi=600)
plt.xlabel("Languages", fontsize=12)
plt.xticks(rotation = 90)
plt.ylabel("Bytes_PPL", fontsize=12)
plt.title("Byte Perplexity of Flores 101 by languages (bloom, opt 175, mgpt)")

plt.rc('font', size=10) #controls default text size
plt.rc('axes', titlesize=10) #fontsize of the title
plt.rc('axes', labelsize=10) #fontsize of the x and y labels
plt.rc('xtick', labelsize=7) #fontsize of the x tick labels
plt.rc('ytick', labelsize=10) #fontsize of the y tick labels
plt.rc('legend', fontsize=10) #fontsize of the legend
plt.legend('Model', loc='upper left')
plt.plot(langcode, bloom176, label='bloom 176')
plt.plot(langcode, opt175, label='opt 175')
plt.plot(langcode, mgpt, label='mgpt')

plt.show()


# Byte perplexity is not appropriate as different scripts use different number of bytes on average. Per byte perplexity gives an edge to languages with 'complex' scripts (utf8-wise) such as thai and vietnamese. It is more fair to simply average the total perplexity / sentence.
# 
# The byte perplexity is computed in [eval_harness](https://github.com/EleutherAI/lm-evaluation-harness/blob/master/lm_eval/metrics.py) as $exp \frac{\sum_x log_2 (p(x))}{\sum l(x)}$ where the sum ranges over (probably) sentences. 
# 
# To remove the byte normalization we should take the log, multiply by the length, divide by N, and exponentiate back.

# In[27]:


import math
n_eng_chars = 132977
n_sent = 1012
flsize = pd.read_csv('Analysis/flores-sizes.csv', sep='\t', names=["lang", "nbytes", "nchars", "nsents"])
# flsize.set_index("lang", inplace=True, verify_integrity=True)
flsize['lang'] = flsize['lang'].apply(lambda s: s.strip())
# print(flsize.head())
# print(flsize.shape)
# print('***',flsize.loc[0,'lang'],'***')

def setmetric(metric):
    return('char_perplexity')

newdf = df[df['metric'] == 'byte_perplexity'].copy(deep=True)
sel.drop_duplicates(inplace=True,ignore_index=True)
# print(newdf.shape)
# print(newdf.head())
newdf["metric"] = newdf["metric"].apply(setmetric)
newdf = newdf.merge(flsize, left_on='lang', right_on = 'lang')
# print(newdf.shape)

newdf['score'] = newdf['score'].apply(math.log)* newdf['nbytes']
sel = newdf.loc[:,['model_name','lang','score']]
print(sel.groupby(['model_name']).describe())

# Normalize by char newdf['score'] = newdf['score'] * newdf['nbytes'] /newdf['nchars']
# Normalize by English Char newdf['score'] = newdf['score'] * newdf['nbytes']/n_eng_chars
newdf['score'] = (newdf['score']/n_eng_chars).apply(math.exp)

print(newdf.head())


# In[28]:


sel = newdf.loc[:,['model_name','lang','score']]
print(sel.groupby(['model_name']).describe())

newlang = sel.pivot(index='lang', columns='model_name', values='score').sort_values(by='bloom176b',axis=0)
print(newlang.sort_values(by='bloom176b',axis=0))


# In[95]:


# Indic language codes: 
# kan (Kannadan)
# tel (Telugu)
# hin (Hindi)
# ben (Bengali)
# mar (Marhati)
# asm (Assamese)
# ori (Odia) -> ory
# guj (Gujarati)
# pan (Punjabi)
# nep (Nepali) -> npy
# mal (Malayalam)
# urd (Urdu)
# tam (Tamil)
langcode = newlang.index.array
bloom176 = newlang['bloom176b'].array
opt175 = newlang['opt175b'].array
mgpt = newlang['mgpt'].array

plt.figure(figsize=(12, 5), dpi=600)
plt.xlabel("Languages", fontsize=12)
plt.xticks(rotation = 90)
plt.ylabel("Logprob", fontsize=12)
plt.title("Average logprob for Flores 101 by languages (bloom = blue, opt 175 = orange, mgpt = green)")

plt.rc('font', size=10) #controls default text size
plt.rc('axes', titlesize=10) #fontsize of the title
plt.rc('axes', labelsize=10) #fontsize of the x and y labels
plt.rc('xtick', labelsize=7) #fontsize of the x tick labels
plt.rc('ytick', labelsize=10) #fontsize of the y tick labels
plt.rc('legend', fontsize=10) #fontsize of the legend
plt.legend('Model', loc='upper left')
plt.plot(langcode[0:102], bloom176[0:102], label='bloom 176')
plt.plot(langcode[0:102], opt175[0:102], label='opt 175')
plt.plot(langcode[0:102], mgpt[0:102], label='mgpt')

plt.show()


# In[99]:


bloomlen = pd.read_csv('Analysis/vocab-analysis/bloom_floresstat_bylang.csv', sep=',').sort_values(by='languages',axis=0) # names=["lang", "nsents", "nchars", "nbytes", "ntokens", "nbpertok", "ncpertok"])
print(bloomlen.head())

mgptlen = pd.read_csv('Analysis/vocab-analysis/mgpt_floresstat_bylang.csv', sep=',').sort_values(by='language',axis=0) # names=["lang", "nsents", "nchars", "nbytes", "ntokens", "nbpertok", "ncpertok"])
mgptlen.head()

optlen = pd.read_csv('Analysis/vocab-analysis/opt_floresstat_bylang.csv', sep=',').sort_values(by='language',axis=0)
mgptlen.head()

langcode = bloomlen['language'].array
bloomtoks = bloomlen['n_token'].array
bloombpt  = bloomlen['char_per_token'].array
opttoks = optlen['n_token'].array
optbpt  = optlen['char_per_token'].array
mgpttoks = mgptlen['n_token'].array
mgptbpt  = mgptlen['char_per_token'].array


# In[100]:


plt.figure(figsize=(12, 5), dpi=600)
plt.xlabel("Languages", fontsize=12)
plt.xticks(rotation = 90)
plt.ylabel("Number of token", fontsize=12)
plt.title("Average number of tokens in Flores 101 by languages (bloom = blue, opt 175 = orange, mgpt = green)")

plt.rc('font', size=10) #controls default text size
plt.rc('axes', titlesize=10) #fontsize of the title
plt.rc('axes', labelsize=10) #fontsize of the x and y labels
plt.rc('xtick', labelsize=7) #fontsize of the x tick labels
plt.rc('ytick', labelsize=10) #fontsize of the y tick labels
plt.rc('legend', fontsize=10) #fontsize of the legend
plt.legend('Model', loc='upper left')
#plt.plot(langcode[0:102], bloombpt[0:102], label='bloom 176')
#plt.plot(langcode[0:102], optbpt[0:102], label='opt 175')
#plt.plot(langcode[0:102], mgptbpt[0:102], label='mgpt')
plt.plot(langcode[0:102], bloomtoks[0:102], label='bloom 176')
plt.plot(langcode[0:102], opttoks[0:102], label='opt 175')
plt.plot(langcode[0:102], mgpttoks[0:102], label='mgpt')

plt.show()


# In[105]:


# open figure + axis
fig, ax = plt.subplots()
# plot
ax.scatter(x=bloomlen['n_token'],y=bloomlen['n_byte'],c='DarkBlue')
# set labels
ax.set_xlabel('number of tokens')
ax.set_ylabel('number of bytes')

# annotate points in axis
for idx, row in bloomlen.iterrows():
    ax.annotate(row['language'], (row['n_token'], row['n_byte']) )
# force matplotlib to draw the graph
plt.show()


# In[ ]:




