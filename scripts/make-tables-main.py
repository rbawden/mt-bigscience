#!/usr/bin/python
import pandas as pd

# load the results files (tsv format) as a dataframe
def load_df(filename, model, postproc, task):
    data = pd.read_csv(filename, delimiter="\t", index_col=False)
    data = data[data["model"] == model]
    data = data[data["task"] == task]
    data = data.fillna("")
    data = data[data["postproc"] == postproc]
    return data


# table of high-resource MT results
def main_comparison(metric, tab_format="latex"):
    data = {}
    for postproc in '', 'newline-cut-custom-truncate':
        data[postproc] = {}
        for dataset, task in [('wmt14_fr_en', 'wmt14_fr_en'), ('wmt14_fr_en', 'wmt14_en_fr'),
                              ('wmt14_hi_en', 'wmt14_hi_en'), ('wmt14_hi_en', 'wmt14_en_hi'),
                               ('diabla', 'diabla'), ('flores-101', 'flores_101_mt')]:
            if dataset == 'diabla':
                if dataset + 'en-fr' not in data[postproc]:
                    data[postproc][dataset + 'en-fr'] = {}
                    data[postproc][dataset + 'fr-en'] = {}
                data[postproc][dataset + 'fr-en'][task] = {0: {}, 1: {}}
                data[postproc][dataset + 'en-fr'][task] = {0: {}, 1: {}}
            else:
                if dataset not in data[postproc]:
                    data[postproc][dataset] = {}
                data[postproc][dataset][task] = {0: {}, 1: {}}
            for shot in [0, 1]:
                for model in 'bloom', 't0', 'mt0-xxl', 'opt':
                    if dataset == "diabla":
                        filename = "outputs/" + dataset + "/" + str(shot) + "-shot/" + metric + "-results"
                        data[postproc][dataset + "en-fr"][task][shot][model] = load_df(filename + ".English-French.tsv", model, postproc, task)
                        data[postproc][dataset + "fr-en"][task][shot][model] = load_df(filename + ".French-English.tsv", model, postproc, task)
                    else:
                        filename = "outputs/" + dataset + "/" + str(shot) + "-shot/" + metric + "-results.tsv"
                        data[postproc][dataset][task][shot][model] = load_df(filename, model, postproc, task)

    def one_row(sub_data, template, colmetric, precision=2):
        list_results = []
        for shot in 0, 1:
            for model in 'bloom', 't0', 'mt0-xxl', 'opt':
                if len(sub_data[shot][model][sub_data[shot][model]['template'] == template][colmetric].values) == 1:
                    value = sub_data[shot][model][sub_data[shot][model]['template'] == template][colmetric].values[0]
                    list_results.append(f"{value:{precision}.{precision}f}")
                else:
                    print('There are multiple values for the same configuration')
                    list_results.append('--')
                    exit()
            if shot == 0:
                list_results.append('')

        return list_results

    # headers
    metric_col = metric.upper()
    spmetric_col = metric_col if metric == 'comet' else 'spBLEU'
    if tab_format == "latex":
        print(r'\begin{table}[!ht]')
    for postproc in ['', 'newline-cut-custom-truncate']:
        res_type = 'Original' if postproc == '' else 'Truncated'
        if tab_format == "latex":
            print(r'''\begin{subtable}[h]{0.48\textwidth}
            \centering\small
            \resizebox{\linewidth}{!}{
            \begin{tabular}{lrrrrrrrrr}
            \toprule
            & \multicolumn{4}{c}{0-shot} && \multicolumn{4}{c}{1-shot} \\
            & \bloom & T0 & mT0-xxl & OPT & \hphantom{} & \bloom & T0 & mT0-xxl & OPT \\
            \midrule''')
    
        # WMT
        if tab_format == "latex":
            print(r'\multicolumn{5}{l}{WMT 2014} \\')
            print(r'\midrule')
        else:
           
            print('\nWMT14 results (' + res_type + ' outputs)')
            print(r'Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |')
            print(r'|---|---|---|---|---|---|')
        task = dataset = 'wmt14_fr_en'
        template = 'xglm-en-fr-source+target'
        row_results = one_row(data[postproc][dataset][task], template, metric_col)
        if tab_format == "latex":
            print(r'en$\rightarrow$fr & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| en→fr | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        template = 'xglm-fr-en-source+target'
        row_results = one_row(data[postproc][dataset][task], template, metric_col)
        if tab_format == "latex":
            print(r'fr$\rightarrow$en & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| fr→en | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        task = dataset = 'wmt14_hi_en'
        template = 'xglm-en-hi-source+target'
        row_results = one_row(data[postproc][dataset][task], template, metric_col)
        if tab_format == "latex":
            print(r'en$\rightarrow$hi & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| en→hi | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        template = 'xglm-hi-en-source+target'
        row_results = one_row(data[postproc][dataset][task], template, metric_col)
        if tab_format == "latex":
            print(r'hi$\rightarrow$en & ' + ' & '.join(row_results) + r' \\')
            print(r'\midrule')
        else:
            print(r'| hi→en | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        
        # Diabla
        dataset, template = 'diabla', 'xglm-source+target'
        if tab_format == "latex":
            print(r'\multicolumn{5}{l}{DiaBLa} \\')
            print(r'\midrule')
        else:
            print('\nDiaBLa results (' + res_type + ' outputs)')
            print(r'Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |')
            print(r'|---|---|---|---|---|---|')
        row_results = one_row(data[postproc][dataset + 'en-fr'][dataset], template, metric_col)
        if tab_format == "latex":
            print(r'en$\rightarrow$fr & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| en→fr | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        row_results = one_row(data[postproc][dataset + 'fr-en'][dataset], template, metric_col)
        if tab_format == "latex":
            print(r'fr$\rightarrow$en & ' + ' & '.join(row_results) + r' \\')
            print(r'\midrule')
        else:
            print(r'| fr→en | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        
        # Flores
        if tab_format == "latex":
            print(r'\multicolumn{5}{l}{Flores-101} \\')
            print(r'\midrule')
        else:
            print('\nFlores-101 results (' + res_type + ' outputs)')
            print(r'Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |')
            print(r'|---|---|---|---|---|---|')
        dataset = 'flores-101'
        template = 'xglm-English-French-source+target'

        row_results = one_row(data[postproc][dataset]['flores_101_mt'], template, spmetric_col)
        if tab_format == "latex":
            print(r'en$\rightarrow$fr & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| en→fr | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        template = 'xglm-French-English-source+target'
        row_results = one_row(data[postproc][dataset]['flores_101_mt'], template, spmetric_col)
        if tab_format == "latex":
            print(r'fr$\rightarrow$en & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| fr→en | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        template = 'xglm-English-Hindi-source+target'
        row_results = one_row(data[postproc][dataset]['flores_101_mt'], template, spmetric_col)
        if tab_format == "latex":
            print(r'en$\rightarrow$hi & ' + ' & '.join(row_results) + r' \\')
        else:
            print(r'| en→hi | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'| | 1 | ' + ' | '.join(row_results[5:]) + ' |')
        template = 'xglm-Hindi-English-source+target'
        
        row_results = one_row(data[postproc][dataset]['flores_101_mt'], template, spmetric_col)
        if tab_format == "latex":
            print(r'hi$\rightarrow$en & ' + ' & '.join(row_results) + r' \\')
        
            print(r'\bottomrule')
            print(r'\end{tabular}}')
            if postproc == '':
                print(r'\caption{\label{tab:xglm-main-orig}')
                print(r'Original predictions}')
            else:
                print(r'\caption{\label{tab:xglm-main-truncated}')
                print(r'Truncated predictions}')
            print(r'\end{subtable}')
        else:
            print(r'| hi→en | 0 | ' + ' | '.join(row_results[:4]) + ' |')
            print(r'|  | 1 | ' + ' | '.join(row_results[5:]) + ' |')
    if tab_format == "latex":
        print(r'\end{table}')


# table format latex or markdown
tab_format='latex'
#tab_format = "markdown"

# print out all tables from this results file
#metric = 'bleu'
metric = 'comet'


# choose one of these and comment the other
#results_file = oubleu_results_file
# results_file = comet_results_file

# print all tables
main_comparison(metric, tab_format)
