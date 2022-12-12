#!/usr/bin/python
import os, json, re
import tabulate
import pandas as pd
from sacrebleu.metrics import BLEU
from pathlib import Path


def get_stderr(examples, metric):
    bootstrap_iters=100000
    stderr = lm_eval.metrics.stderr_for_metric(metric,
                                               bootstrap_iters=min(bootstrap_iters, 1000)
                                               if metric in ["bleu", "chrf", "ter"] else bootstrap_iters)
    return stderr(examples)

def get_docid2lang(xglm_examples):
    '''
    Return the correspondence between document ids and their language direction by using the xglm zero-shot prompt
    '''
    docid2lang = {}
    for example in xglm_examples:
        docid2lang[example['doc_id']] = {'English': 'en2fr', 'French': 'fr2en'}[re.match('.+?###\n(English|French)', example['ctx'], re.DOTALL).group(1)]
    return docid2lang

def bleu_score(sys_sents, trg_sents):
    '''
    Calculate BLEU using default settings
    '''
    bleu = BLEU()
    score = bleu.corpus_score(sys_sents, [[x[0] for x in trg_sents]])
    return score.score

def get_sys_and_trg(examples, docid2lang, langdir=None):
    '''
    Return a list of system hypotheses and a list of their corresponding target translations.
    If langdir is not specified (i.e. None) return all examples, otherwise it should be set as
    en2fr or fr2en and in this case only the examples from that language direction are returned.
    '''
    sys_examples, trg_examples = [], []
    for example in examples:
        if langdir is None or docid2lang[example['doc_id']] == langdir:
            sys_examples.append(example['pred'])
            trg_examples.append(example['target'])
    return sys_examples, trg_examples

def calculate_bleu_scores(descr2examples, docid2lang):
    '''
    Calculate BLEU results for all runs for each language direction
    '''
    descr2results = {}
    for descr in descr2examples:
        descr2results[descr] = {}
        for langdir in 'en2fr', 'fr2en':
            sys_examples, trg_examples = get_sys_and_trg(descr2examples[descr], docid2lang, langdir)
            print(langdir, descr, len(sys_examples), len(trg_examples))
            descr2results[descr][langdir] = bleu_score(sys_examples, trg_examples)
    return descr2results
        
def recalculate_all_scores(model2examples):
    model2results = {}
    for model in model2examples:
        model2results[model] = {}
        for prompt in model2examples[model]:
            metric = model2examples[model][prompt]['metric']
            examples = model2examples[model][prompt]['examples']
            if metric == 'acc':
                acc, norm_acc = recalculate_score_acc(examples)
                model2results[model][prompt + ' (acc)'] = str(round(acc, 2))
                model2results[model][prompt + ' (acc_norm)'] = str(round(norm_acc, 2))
            elif metric == 'bleu':
                model2results[model][prompt + ' (bleu)'] = str(round(recalculate_score_bleu(examples), 2))
            #stderr = get_stderr(examples, metric)
    return model2results


def get_description(path):
    '''
    Get description of run (model name, task, template name, number of few-shot, seed)
    '''
    print(path)
    mobj = re.match('.*?model=(.+?)\.task=(.+?)\.templates=(.+?)\.fewshot=(\d+)\..*?seed=(\d+)*', str(path))
    return (mobj.group(1), mobj.group(2), mobj.group(3), mobj.group(4), mobj.group(5))

def read_all_examples(results_file, newline_cut=False):
    '''
    Read all example files in the results folder (both zero-shot and 1-shot)
    '''
    descr2examples = {}
    for path in Path(results_file).rglob('*examples*.jsonl'):
        descr = get_description(path)
        descr2examples[descr] = []
        with open(path) as fp:
            for line in fp:
                example = json.loads(line)
                if newline_cut:
                    example['pred'] = example['pred'].split('\n')[0] 
                descr2examples[descr].append(example)

    return descr2examples

def print_results(descr2results, langdir='en2fr'):
    template2model2result = {}
    for descr in descr2results:
        model, task, template, fewshot, _ = descr
        runkey = task + '-' + template + '-' + fewshot
        if runkey not in template2model2result:
            template2model2result[runkey] = {}
        if model not in template2model2result[runkey]:
            template2model2result[runkey][model] = descr2results[descr][langdir]

    df = pd.DataFrame(template2model2result)
    df.index.name = 'Run type (task, template, fewshot)'
    df = df.fillna('-')
    print(df.transpose())

    
            
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--results_dir', default='examples-per-task/diabla')
    parser.add_argument('-n', '--newline_cut', help='cut on first newline character', default=False, action='store_true')
    args = parser.parse_args()

    # read all results files
    descr2examples = read_all_examples(args.results_dir, args.newline_cut)
    docid2lang = get_docid2lang(descr2examples[('bloom', 'diabla', 'xglm', '1', '1234')])
    
    # calculate BLEU scores for en2fr and fr2en
    descr2results = calculate_bleu_scores(descr2examples, docid2lang)
    print('******* en2fr *******')
    print_results(descr2results, 'en2fr')
    print('\n******* fr2en *******')
    print_results(descr2results, 'fr2en')



