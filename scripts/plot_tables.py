#!/usr/bin/python
import pandas as pd

lang2code = {'Galician': 'gl', 'Latin American Spanish': 'es', 'Brazilian Portuguese': 'pt', 'Bengali': 'bn',
             'Indonesian': 'id', 'simplified Chinese': 'zh'}

def load_df(filename, model, postproc, task):
    data = pd.read_csv(results_file, delimiter='\t', index_col=False)
    data = data[data['model'] == model] 
    data = data[data['task'] == task]
    data = data.fillna('')
    data = data[data['postproc'] == postproc]
    return data

def table_highresource(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')
    
    # store results
    langs = ['English', 'Arabic', 'French', 'simplified Chinese', 'Latin American Spanish']
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data['template'] == 'flores-xglm-' + lang1 + '-' + lang2]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = '--'
                else:
                    lang2lang[lg1][lg2] = result['spBLEU'].values[0]
            else:
                lang2lang[lg1][lg2] = '--'
                
    # get table
    print(r'Src \ Trg & ' + ' & '.join(sorted(lang2lang)) + r' \\')
    print(r'\midrule')
    for lang in sorted(lang2lang):
        results = ["%.2f" % round(lang2lang[lang][trg], 2) if lang2lang[lang][trg] != '--' else '--' for trg in sorted(lang2lang)]
        print('\multirow{2}{*}{' + lang + r'} & \bloom & ' + ' & '.join(results) + r' \\')
        print(r'\midrule')
    print('\n\n')

def table_romance_langs(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')
    
    # store results
    langs = ['Catalan', 'Latin American Spanish', 'French', 'Galician', 'Brazilian Portuguese', 'Italian']
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data['template'] == 'flores-xglm-' + lang1 + '-' + lang2]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = '--'
                else:
                    lang2lang[lg1][lg2] = result['spBLEU'].values[0]
            else:
                lang2lang[lg1][lg2] = '--'
                
    # get table
    print(r'Src \ Trg & ' + ' & '.join(sorted(lang2lang)) + r' \\')
    print(r'\midrule')
    for lang in sorted(lang2lang):
        results = ["%.2f" % round(lang2lang[lang][trg], 2) if lang2lang[lang][trg] != '--' else '--' for trg in sorted(lang2lang)]
        print('\multirow{2}{*}{' + lang + r'} & \bloom & ' + ' & '.join(results) + r' \\')
        print(r'\midrule')
    print('\n\n')

def table_lowresource(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')
    
    #print(data[data.duplicated(keep=False)]) # check duplicated
    # store results                                                                                                                                  
    langs = ['English', 'Bengali', 'Hindi', 'Swahili', 'Yoruba']
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data['template'] == 'flores-xglm-' + lang1 + '-' + lang2]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = '--'
                else:
                    lang2lang[lg1][lg2] = result['spBLEU'].values[0]
            else:
                lang2lang[lg1][lg2] = '--'

    # get table
    lang_codes = [lang2code.get(x, x[:2].lower()) for x in langs]
    print(r'Src \ Trg & ' + ' & '.join(lang_codes) + r' \\')
    print(r'\midrule')
    for lang in lang_codes:
        results = ["%.2f" % round(lang2lang[lang][trg], 2) if lang2lang[lang][trg] != '--' else '--' for trg in lang_codes]
        print('\multirow{2}{*}{' + lang + r'} & \bloom & ' + ' & '.join(results) + r' \\')
        print(r'\midrule')
    print('\n\n')



def table_midresource(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')
    
    #print(data[data.duplicated(keep=False)]) # check duplicated
    # store results                                                                                                                                  
    langs = ['English', 'French', 'Hindi', 'Indonesian', 'Vietnamese']
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data['template'] == 'flores-xglm-' + lang1 + '-' + lang2]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = '--'
                else:
                    lang2lang[lg1][lg2] = result['spBLEU'].values[0]
            else:
                lang2lang[lg1][lg2] = '--'

    # get table
    lang_codes = [lang2code.get(x, x[:2].lower()) for x in langs]
    print(r'Src \ Trg & ' + ' & '.join(lang_codes) + r' \\')
    print(r'\midrule')
    for lang in lang_codes:
        results = ["%.2f" % round(lang2lang[lang][trg], 2) if lang2lang[lang][trg] != '--' else '--' for trg in lang_codes]
        print('\multirow{2}{*}{' + lang + r'} & \bloom & ' + ' & '.join(results) + r' \\')
        print(r'\midrule')
    print('\n\n')
    
results_file = 'outputs/flores-101/1-shot/bleu-results.tsv'
table_romance_langs(results_file)
table_lowresource(results_file)
table_midresource(results_file)
table_highresource(results_file)
