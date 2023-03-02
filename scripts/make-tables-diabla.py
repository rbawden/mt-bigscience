#!/usr/bin/python
import pandas as pd

# load the results files (tsv format) as a dataframe
def load_df(filename, model):
    print(filename)
    data = pd.read_csv(filename, delimiter="\t", index_col=False)
    print(data)
    data = data[data["model"] == model]
    #data = data[data["task"] == task]
    data = data.fillna("")
    #data = data[data["postproc"] == postproc]
    return data


def context_table(bleu_results_file_enfr, bleu_results_file_fren,
                 comet_results_file_enfr, comet_results_file_fren, tab_format='latex'):
    data = {'bleu': {'enfr': load_df(bleu_results_file_enfr, 'bloom'),
                     'fren': load_df(bleu_results_file_fren, 'bloom')},
            'comet': {'enfr': load_df(comet_results_file_enfr, 'bloom'),
                      'fren': load_df(comet_results_file_fren, 'bloom')}}

    if tab_format == "latex":
        print(r'''\begin{table}[!ht]
        \centering\small
        \resizebox{\linewidth}{!}{
        \begin{tabular}{lllrrrr}
        \toprule
        \multicolumn{2}{c}{1-shot example} & & \multicolumn{2}{c}{en$\rightarrow$fr} & \multicolumn{2}{c}{fr$\rightarrow$en} \\
        Origin & Direction & Truncate & BLEU & COMET & BLEU & COMET \\
        \toprule''')
    else:
        print(r'| Origin | Direction | Truncate | en→fr BLEU | en→fr COMET | fr→en BLEU | fr→en COMET |')
        print(r'|---|---|---|---|---|---|---|')

    def one_row(task, postproc):
        results = []
        for lang in 'enfr', 'fren':
            for metric in 'bleu', 'comet':
                precision = 4 if metric == "comet" else 2
                sub_data = data[metric][lang][data[metric][lang]['postproc'] == postproc]
                value = sub_data[sub_data['task'] == task][metric.upper()].values[0]
                results.append(f"{value:{precision}.{precision}f}")
        return results
    
    row_results = one_row('diabla', '')
    if tab_format == "latex":
        print(r'\multirow{2}{*}{Rand.} & \multirow{2}{*}{rand.} & $\times$ & ' + ' & '.join(row_results) + r' \\')
    else:
        print(r'| Rand. | rand. | ❌ | ' + ' | '.join(row_results) + r' |')
    row_results = one_row('diabla', 'newline-cut-custom-truncate')
    if tab_format == "latex":
        print(r'&  & $\checkmark$ & ' + ' & '.join(row_results) + r' \\')
        print(r'\midrule')
    else:
        print(r'| | | ✅ | ' + ' | '.join(row_results) + r' |')
    row_results = one_row('diabla_1_shot_context_random', '')
    if tab_format == "latex":
        print(r'\multirow{2}{*}{Prev.} & \multirow{2}{*}{rand.} &  $\times$ & ' + ' & '.join(row_results) + r' \\')
    else:
        print(r'| Prev. | rand. | ❌ | ' + ' | '.join(row_results) + r' |')
    row_results = one_row('diabla_1_shot_context_random', 'newline-cut-custom-truncate')
    if tab_format == "latex":
        print(r' & & $\checkmark$ & ' + ' & '.join(row_results) + r' \\')
        print(r'\midrule')
    else:
        print(r'| | | ✅ | ' + ' | '.join(row_results) + r' |')
        
    row_results = one_row('diabla_1_shot_context_same', '')
    if tab_format == "latex":
        print(r'\multirow{2}{*}{Prev.} & \multirow{2}{*}{same} & $\times$ & ' + r' & '.join(row_results) + r' \\')
    else:
         print(r'| Prev. | Same | ❌ | ' + ' | '.join(row_results) + r' |')
    row_results = one_row('diabla_1_shot_context_same', 'newline-cut-custom-truncate')
    if tab_format == "latex":
        print(r'&  & $\checkmark$ & \textbf{' + r'} & \textbf{'.join(row_results) + r'} \\')
        print(r'\midrule')
    else:
        print(r'| | | ✅ | ' + ' | '.join(row_results) + r' |')
    row_results = one_row('diabla_1_shot_context_opposite', '')
    if tab_format == "latex":
        print(r'\multirow{2}{*}{Prev.} & \multirow{2}{*}{opp.} & $\times$ & ' + ' & '.join(row_results) + r' \\')
    else:
        print(r'| Prev. | Opposite | ❌ | ' + ' | '.join(row_results) + r' |')
    row_results = one_row('diabla_1_shot_context_opposite', 'newline-cut-custom-truncate')
    if tab_format == "latex":
        print(r'& & $\checkmark$ & ' + ' & '.join(row_results) + r' \\')
    else:
        print(r'| | | ✅ | ' + ' | '.join(row_results) + r' |')
    if tab_format == "latex":    
        print(r'''\bottomrule
        \end{tabular}}
        \caption{Comparison of 1-shot results (BLEU) for the DiaBLa dataset when using the previous sentence or a random sentence for the 1-shot example (using the \texttt{xglm-source+target} prompt). In bold are the best results for each language direction.}
        \label{tab:diabla-context-results}
        \end{table}''')

# table format latex or markdown
# tab_format='latex'
tab_format = "markdown"

# print out all tables from this results file
bleu_results_file_enfr = "outputs/diabla/1-shot/bleu-results.English-French.tsv"
bleu_results_file_fren = "outputs/diabla/1-shot/bleu-results.French-English.tsv"
comet_results_file_enfr = "outputs/diabla/1-shot/comet-results.English-French.tsv"
comet_results_file_fren = "outputs/diabla/1-shot/comet-results.French-English.tsv"

context_table(bleu_results_file_enfr, bleu_results_file_fren,
              comet_results_file_enfr, comet_results_file_fren, tab_format=tab_format)
