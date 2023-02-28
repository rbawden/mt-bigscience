#!/usr/bin/pythonA
import pandas as pd

lang2code = {
    "Galician": "gl",
    "Latin American Spanish": "es",
    "Brazilian Portuguese": "pt",
    "Bengali": "bn",
    "Indonesian": "id",
    "simplified Chinese": "zh",
}

# load the results files (tsv format) as a dataframe
def load_df(filename, model, postproc, task):
    data = pd.read_csv(filename, delimiter="\t", index_col=False)
    data = data[data["model"] == model]
    data = data[data["task"] == task]
    data = data.fillna("")
    data = data[data["postproc"] == postproc]
    return data


# table of high-resource MT results
def table_highresource(results_file, model="bloom", postproc="", tab_format="latex"):
    data = load_df(results_file, model, postproc, "flores_101_mt")
    m2m = {
        "ar": {"en": 25.50, "es": 16.74, "fr": 25.69, "zh": 13.10},
        "en": {"ar": 17.92, "es": 25.57, "fr": 41.99, "zh": 19.33},
        "es": {"ar": 12.11, "en": 25.09, "fr": 29.33, "zh": 14.86},
        "fr": {"ar": 15.36, "en": 37.17, "es": 25.60, "zh": 17.61},
        "zh": {"ar": 11.55, "en": 20.91, "es": 16.92, "fr": 24.32},
    }

    # store results
    langs = [
        "English",
        "Arabic",
        "French",
        "simplified Chinese",
        "Latin American Spanish",
    ]
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data["template"] == "xglm-" + lang1 + "-" + lang2 + "-source+target"]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = "--"
                else:
                    lang2lang[lg1][lg2] = result["spBLEU"].values[0]
            else:
                lang2lang[lg1][lg2] = "--"

    # print latex table
    precision = 4 if "comet" in results_file else 2
    if tab_format == "latex":
        print(r"\scalebox{0.85}{")
        print(r"\begin{tabular}{llrrrrr}")
        print(r"\toprule")
        print(r"Src $\downarrow$ & Trg $\rightarrow$ & " + " & ".join(sorted(lang2lang)) + r" \\")
    else:
        print("| Src↓ | Trg→ | " + " | ".join(sorted(lang2lang)) + " |")
        print("|" + "---|" * (len(lang2lang) + 2))

    for lang in sorted(lang2lang):
        results = [f"{round(lang2lang[lang][trg], precision):{precision}.{precision}f}"
                   if lang2lang[lang][trg] != "--" else "--" for trg in sorted(lang2lang)]
        m2m_results = [f"{round(m2m[lang][trg], precision):{precision}.{precision}f}"
                       if trg in m2m[lang] else "--" for trg in sorted(lang2lang)]
        if tab_format == "latex":
            print(r"\midrule")
            print(r"\multirow{2}{*}{" + lang + r"} & \bloom & " + " & ".join(results) + r" \\")
            print(r" & M2M & " + " & ".join(m2m_results) + r" \\")
        else:
            print(" | " + lang + " | Bloom | " + " | ".join(results) + " |")
            print(" |  | M2M | " + " | ".join(m2m_results) + " |")

    if tab_format == "latex":
        print(r"\bottomrule")
        print(r"\end{tabular}}")
        print(r"\caption{High-resource language pairs.}")
        print(r"\label{tab:flores101_summary:high-high}")
    print("\n\n")


# table of mid-high-resource MT results
def table_midresource(results_file, model="bloom", postproc=""):
    data = load_df(results_file, model, postproc, "flores_101_mt")
    m2m = {
        "en": {"fr": 41.99, "hi": 28.15, "id": 37.26, "vi": 35.10},
        "fr": {"en": 37.17, "hi": 22.91, "id": 29.14, "vi": 30.26},
        "hi": {"en": 27.89, "fr": 25.88},
        "id": {"en": 33.74, "fr": 30.81},
        "vi": {"en": 29.51, "fr": 25.82},
    }

    # print(data[data.duplicated(keep=False)]) # check duplicated
    # store results
    langs = ["English", "French", "Hindi", "Indonesian", "Vietnamese"]
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[
                    data["template"] == "xglm-" + lang1 + "-" + lang2 + "-source+target"
                ]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = "--"
                else:
                    lang2lang[lg1][lg2] = result["spBLEU"].values[0]
            else:
                lang2lang[lg1][lg2] = "--"

    # print latex table
    precision = 4 if "comet" in results_file else 2
    lang_codes = [lang2code.get(x, x[:2].lower()) for x in langs]
    if tab_format == "latex":
        print(r"\scalebox{0.85}{")
        print(r"\begin{tabular}{llrrrrr}")
        print(r"\toprule")
        print(r"Src $\downarrow$ & Trg $\rightarrow$ & " + " & ".join(lang_codes) + r" \\")
    else:
        print("| Src↓ | Trg→ | " + " | ".join(sorted(lang_codes)) + " |")
        print("|" + "---|" * (len(lang2lang) + 2))

    for lang in lang_codes:
        results = [f"{round(lang2lang[lang][trg], precision):{precision}.{precision}f}"
                   if lang2lang[lang][trg] != "--" else "--" for trg in lang_codes]
        m2m_results = [f"{round(m2m[lang][trg], precision):{precision}.{precision}f}"
                       if trg in m2m[lang] else "--" for trg in sorted(lang_codes)]
        if tab_format == "latex":
            print(r"\midrule")
            print(r"\multirow{2}{*}{" + lang + r"} & \bloom & " + " & ".join(results) + r" \\")
            print(r" & M2M & " + " & ".join(m2m_results) + r" \\")
        else:
            print(" | " + lang + " | Bloom | " + " | ".join(results) + " |")
            print(" |  | M2M | " + " | ".join(m2m_results) + " |")
    if tab_format == "latex":
        print(r"\bottomrule")
        print(r"\end{tabular}}")
        print(r"\caption{High$\rightarrow$mid-resource language pairs.}")
        print(r"\label{tab:flores101:high-mid}")
    print("\n\n")


# table of low-resource MT results
def table_lowresource(results_file, model="bloom", postproc=""):
    data = load_df(results_file, model, postproc, "flores_101_mt")
    m2m = {
        "en": {"bn": 23.04, "hi": 28.15, "sw": 26.95, "yo": 2.17},
        "bn": {"en": 22.86, "hi": 21.76},
        "hi": {"en": 27.89, "bn": 21.77},
        "sw": {"en": 30.43, "yo": 1.29},
        "yo": {"en": 4.18, "sw": 1.93},
    }

    # print(data[data.duplicated(keep=False)]) # check duplicated
    # store results
    langs = ["English", "Bengali", "Hindi", "Swahili", "Yoruba"]
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data["template"] == "xglm-" + lang1 + "-" + lang2 + "-source+target"]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = "--"
                else:
                    lang2lang[lg1][lg2] = result["spBLEU"].values[0]
            else:
                lang2lang[lg1][lg2] = "--"

    # get latex table
    precision = 4 if "comet" in results_file else 2
    lang_codes = [lang2code.get(x, x[:2].lower()) for x in langs]
    if tab_format == "latex":
        print(r"\scalebox{0.86}{")
        print(r"\begin{tabular}{llrrrrr}")
        print(r"\toprule")
        print(r"Src$\downarrow$ & Trg$\rightarrow$ & " + " & ".join(lang_codes) + r" \\")
    else:
        print("| Src↓ | Trg→ | " + " | ".join(sorted(lang_codes)) + " |")
        print("|" + "---|" * (len(lang2lang) + 2))
    for lang in lang_codes:
        results = [
            f"{round(lang2lang[lang][trg], precision):{precision}.{precision}f}"
            if lang2lang[lang][trg] != "--"
            else "--"
            for trg in lang_codes
        ]
        m2m_results = [
            f"{round(m2m[lang][trg], precision):{precision}.{precision}f}"
            if trg in m2m[lang]
            else "--"
            for trg in lang_codes
        ]
        if tab_format == "latex":
            print(r"\midrule")
            print(r"\multirow{2}{*}{" + lang + r"} & \bloom & " + " & ".join(results) + r" \\")
            print(r" & M2M & " + " & ".join(m2m_results) + r" \\")
        else:
            print(" | " + lang + " | Bloom | " + " | ".join(results) + " |")
            print(" |  | M2M | " + " | ".join(m2m_results) + " |")

    if tab_format == "latex":
        print(r"\bottomrule")
        print(r"\end{tabular}}")
        print(r"\caption{Low-resource languages}")
        print(r"\label{tab:flores101_summary:high-low}")
    print("\n\n")


# table of Romance lang MT results
def table_romance_langs(results_file, model="bloom", postproc=""):
    data = load_df(results_file, model, postproc, "flores_101_mt")
    m2m = {
        "ca": {"es": 25.17, "fr": 35.08, "gl": 33.42, "it": 25.50, "pt": 35.17},
        "es": {"ca": 23.12, "fr": 29.33, "gl": 27.54, "it": 23.87, "pt": 28.10},
        "fr": {"ca": 28.74, "es": 25.60, "gl": 32.82, "it": 28.56, "pt": 37.84},
        "gl": {"ca": 30.07, "es": 27.65, "fr": 37.06, "it": 26.87, "pt": 34.81},
        "it": {"ca": 25.20, "es": 29.23, "fr": 34.39, "gl": 29.23, "pt": 31.47},
        "pt": {"ca": 30.69, "es": 26.88, "fr": 40.17, "gl": 33.77, "it": 28.09},
    }

    # store results
    langs = [
        "Catalan",
        "Latin American Spanish",
        "French",
        "Galician",
        "Brazilian Portuguese",
        "Italian",
    ]
    lang2lang = {}
    for lang1 in langs:
        lg1 = lang2code.get(lang1, lang1[:2].lower())
        lang2lang[lg1] = {}
        for lang2 in langs:
            lg2 = lang2code.get(lang2, lang2[:2].lower())
            if lang1 != lang2:
                result = data[data["template"] == "xglm-" + lang1 + "-" + lang2 + "-source+target"]
                assert len(result) <= 1
                if len(result) == 0:
                    lang2lang[lg1][lg2] = "--"
                else:
                    lang2lang[lg1][lg2] = result["spBLEU"].values[0]
            else:
                lang2lang[lg1][lg2] = "--"

    # print latex table
    precision = 4 if "comet" in results_file else 2
    if tab_format == "latex":
        print(r"\resizebox{\linewidth}{!}{")
        print(r"\begin{tabular}{llrrrrrr}")
        print(r"\toprule")
        print(r"Src$\downarrow$ & Trg$\rightarrow$ & " + " & ".join(sorted(lang2lang)) + r" \\")
    else:
        print("| Src↓ | Trg→ | " + " | ".join(sorted(lang2lang)) + " |")
        print("|" + "---|" * (len(lang2lang) + 2))
    for lang in sorted(lang2lang):
        results = [
            f"{round(lang2lang[lang][trg], precision):{precision}.{precision}f}"
            if lang2lang[lang][trg] != "--" else "--" for trg in sorted(lang2lang)]
        m2m_results = [f"{round(m2m[lang][trg], precision):{precision}.{precision}f}"
                       if trg in m2m[lang] else "--" for trg in sorted(lang2lang)]
        if tab_format == "latex":
            print(r"\midrule")
            print(r"\multirow{2}{*}{" + lang + r"} & \bloom & " + " & ".join(results) + r" \\")
            print(r" & M2M & " + " & ".join(m2m_results) + r" \\")
        else:
            print(" | " + lang + " | Bloom | " + " | ".join(results) + " |")
            print(" |  | M2M | " + " | ".join(m2m_results) + " |")
    if tab_format == "latex":
        print(r"\bottomrule")
        print(r"\end{tabular}}")
        print(r"\caption{Romance languages}")
        print(r"\label{tab:flores101_summary:same-family}")
    print("\n\n")


def table_transfer(bleu_results_file, comet_results_file):
    model = "bloom"

    if tab_format == "latex":
        print(r"\begin{table}[!ht]")
        print(r"\centering\small")
        print(r"\resizebox{\linewidth}{!}{")
        print(r"\begin{tabular}{llrrrr}")
        print(r"\toprule")
        print(r"                &  & \multicolumn{2}{c}{Original} & \multicolumn{2}{c}{Truncated} \\")
        print(r"\multicolumn{2}{l}{1-shot example direction type} & spBLEU & COMET & spBLEU & COMET \\")
        print(r"\midrule")
    else:
        print("| 1-shot example direction type | 1-shot example direction | spBLEU orig. | COMET orig. | spBLEU trunc. | COMET trunc. |")
        print("|" + "---|" * 6)

    def list_results(task, template):
        bleu_data_orig = load_df(bleu_results_file, model, "", task)
        comet_data_orig = load_df(comet_results_file, model, "", task)
        bleu_data_trunc = load_df(bleu_results_file, model, "newline-cut-custom-truncate", task)
        comet_data_trunc = load_df(comet_results_file, model, "newline-cut-custom-truncate", task)

        return ["%.2f" % round(bleu_data_orig[bleu_data_orig["template"] == template]["spBLEU"].values[0], 2),
                "%.4f" % round(comet_data_orig[comet_data_orig["template"] == template]["comet"].values[0], 4),
                "%.2f" % round(bleu_data_trunc[bleu_data_trunc["template"] == template]["spBLEU"].values[0], 2),
                "%.4f" % round(comet_data_trunc[comet_data_trunc["template"] == template]["comet"].values[0], 4)]

    results = list_results("flores_101_mt", "xglm-Bengali-English-source+target")
    if tab_format == "latex":
        print(r"Same & bn$\rightarrow$en & " + " & ".join(results) + r" \\")
    else:
        print("| Same | bn→en | " + " | ".join(results) + " |")
    results = list_results("flores_101_mt_fewshot_en2bn", "xglm-Bengali-English-source+target")
    if tab_format == "latex":
        print(r"Opposite & en$\rightarrow$bn & " + " & ".join(results) + r" \\")
        print(r"\midrule")
    else:
        print("| Opposite | en→bn | " + " | ".join(results) + " |")
    results = list_results("flores_101_mt_fewshot_hi2en", "xglm-Bengali-English-source+target")
    if tab_format == "latex":
        print(r"Related source & hi$\rightarrow$en & " + " & ".join(results) + r" \\")
    else:
        print("| Related source | hi→en | " + " | ".join(results) + " |")
    results = list_results("flores_101_mt_fewshot_wmt_hi2en", "xglm-Bengali-English-source+target")
    if tab_format == "latex":
        print(r"Related source (from WMT) & hi$\rightarrow$en & " + " & ".join(results) + r" \\")
    else:
        print("| Related source (from WMT) | hi→en | " + " | ".join(results) + " |")
    results = list_results("flores_101_mt_fewshot_fr2en", "xglm-Bengali-English-source+target")
    if tab_format == "latex":
        print(r"HR unrelated source & fr$\rightarrow$en & " + " & ".join(results) + r" \\")
    else:
        print("| HR unrelated source | fr→en | " + " | ".join(results) + " |")
    results = list_results(
        "flores_101_mt_fewshot_fr2ar", "xglm-Bengali-English-source+target"
    )
    if tab_format == "latex":
        print(r"HR unrelated source & fr$\rightarrow$ar & " + " & ".join(results) + r" \\")
        print(r"\bottomrule")
        print(r"\end{tabular}}")
        print(r"\caption{\label{tab:bn-en-fewshot-variation}1-shot results for Flores bn$\rightarrow$en when varying the language direction of 1-shot examples. HR=high-resource.}")
        print(r"\end{table}")
    else:
        print("| HR unrelated source | fr→ar | " + " | ".join(results) + " |")


# choose which type of postprocessing to include (original or truncated)
postproc = ""  # original
# postproc='newline-cut-custom-truncate' # truncated

# table format latex or markdown
# tab_format='latex'
tab_format = "markdown"

# print out all tables from this results file
bleu_results_file = "outputs/flores-101/1-shot/bleu-results.tsv"
comet_results_file = "outputs/flores-101/1-shot/comet-results.tsv"

# choose one of these and comment the other
results_file = bleu_results_file
# results_file = comet_results_file

# print all tables
table_highresource(results_file, postproc=postproc, tab_format=tab_format)
table_midresource(results_file, postproc=postproc)

table_lowresource(results_file, postproc=postproc)
table_romance_langs(results_file, postproc=postproc)

# this table always uses both original and truncated for both comet and bleu so they are not specified
table_transfer(bleu_results_file, comet_results_file)
