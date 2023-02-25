# MT@BigScience

Evaluation results for Machine Translation within the BigScience project

## Outputs and evaluation

### Extract all predictions and evaluate

```
python scripts/process_results_{flores,diabla,wmt}.py
```

This extracts all predictions from .jsonl files into .tsv files and calculates BLEU and COMET scores. These are written out to the following folders:
- `outputs/{wmt14_hi_en,wmt14_fr_en,flores-101}/{0,1,2,5}-shot/{comet,bleu}-results.tsv` for WMT and flores-101
- `outputs/diabla/{0,1}-shot/{comet,bleu}-results.{English-French,French-English}.tsv` for DiaBLa.

Generate latex tables:
```
python scripts/make-tables-flores.py
```

TODO:
- script to generate all eval tables
- check that slurm scripts work (they have been cleaned up a bit) and that they run with the right number of GPUs and amount of memory
- add citation
- make sure all outputs present
- generate BLEU and COMET scores
- add tables to README with results?
