#!/usr/bin/python
import pandas as pd

lang2code = {'Galician': 'gl', 'Latin American Spanish': 'es', 'Brazilian Portuguese': 'pt'}

def plot_romance_langs(results_file, model='bloom'):
    data = pd.read_csv(results_file, delimiter='\t', index_col=False)
    data = data[data['model'] == model] # limit to a specific model
    data = data[data['task'] == 'flores_101_mt'] # limit to the main task
    lang2lang = {}
    langs = ['Catalan', 'Latin American Spanish', 'French', 'Galician', 'Brazilian Portuguese']
    print(data)
    for lang1 in langs:
        lang2lang[lang1] = {}
        for lang2 in langs:
            if lang1 != lang2:
                print(data['template'] =='flores-xglm-' + lang1 + '-' + lang2)
                lang2lang[lang1][lang2] = data[data['template'] == 'flores-xglm-' + lang1 + '-' + lang2]
                
            else:
                lang2lang[lang1][lang2] = '--'
    
    print(data)

results_file = 'outputs/flores-101/1-shot/bleu-results.tsv'
plot_romance_langs(results_file)
