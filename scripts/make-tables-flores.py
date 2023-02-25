#!/usr/bin/python
import pandas as pd

lang2code = {'Galician': 'gl', 'Latin American Spanish': 'es', 'Brazilian Portuguese': 'pt', 'Bengali': 'bn',
             'Indonesian': 'id', 'simplified Chinese': 'zh'}

# load the results files (tsv format) as a dataframe
def load_df(filename, model, postproc, task):
    data = pd.read_csv(results_file, delimiter='\t', index_col=False)
    data = data[data['model'] == model] 
    data = data[data['task'] == task]
    data = data.fillna('')
    data = data[data['postproc'] == postproc]
    return data

# table of high-resource MT results
def table_highresource(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')

    # M2M scores
    m2m = {'ar': {'en': 25.50, 'es': 16.74, 'fr': 25.69, 'zh': 13.10},
           'en': {'ar': 17.92, 'es': 25.57, 'fr': 41.99, 'zh': 19.33},
           'es': {'ar': 12.11, 'en': 25.09, 'fr': 29.33, 'zh': 14.86},
           'fr': {'ar': 15.36, 'en': 37.17, 'es': 25.60, 'zh': 17.61},
           'zh': {'ar': 11.55, 'en': 20.91, 'es': 16.92, 'fr': 24.32}}
    
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

# table of Romance lang MT results
def table_romance_langs(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')

    m2m = {'ca': {'es': 25.17, 'fr': 35.08, 'gl': 33.42, 'it': 25.50, 'pt': 35.17},
           'es': {'ca': 23.12, 'fr': 29.33, 'gl': 27.54, 'it': 23.87, 'pt': 28.10},
           'fr': {'ca': 28.74, 'es': 25.60, 'gl': 32.82, 'it': 28.56, 'pt': 37.84},
           'gl': {'ca': 30.07, 'es': 27.65, 'fr': 37.06, 'it': 26.87, 'pt': 34.81},
           'it': {'ca': 25.20, 'es': 29.23, 'fr': 34.39, 'gl': 29.23, 'pt': 31.47},
           'pt': {'ca': 30.69, 'es': 26.88, 'fr': 40.17, 'gl': 33.77, 'it': 28.09}}
    
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

# table of low-resource MT results
def table_lowresource(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')


    m2m = {'en': {'bn': 23.04, 'hi': 28.15, 'sw': 26.95, 'yo': 2.17},
           'bn': {'en': 22.86, 'hi': 21.76},
           'hi': {'en': 27.89, 'bn': 21.77},
           'sw': {'en': 30.43, 'yo': 1.29},
           'yo': {'en': 4.18, 'sw': 1.93}}
    
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


# table of mid-high-resource MT results
def table_midresource(results_file, model='bloom', postproc=''):
    data = load_df(results_file, model, postproc, 'flores_101_mt')

    m2m = {'en': {'fr': 41.99, 'hi': 28.15, 'id': 37.26,'vi': 35.10},
           'fr': {'en': 37.17 ,'hi': 22.91, 'id': 29.14,'vi': 30.26},
           'hi': {'en': 27.89, 'fr': 25.88},
           'id': {'en': 33.74, 'fr': 30.81},
           'vi': {'en': 29.51, 'fr': 25.82}}
    
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

# print out all tables from this results file
results_file = 'outputs/flores-101/1-shot/bleu-results.tsv'
table_romance_langs(results_file)
table_lowresource(results_file)
table_midresource(results_file)
table_highresource(results_file)
