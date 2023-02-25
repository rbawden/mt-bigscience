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

## Results

### High-resource
(Original outputs with no postprocessing)

| Src↓ | Trg→ | ar|en|es|fr|zh|
|---|---|---|---|---|---|---|
 | ar | Bloom | --|40.28|23.32|33.12|17.68| 
 | ar | M2M | --|25.50|16.74|25.69|13.10| 
 | en | Bloom | 28.21|--|29.42|44.99|26.69| 
 | en | M2M | 17.92|--|25.57|41.99|19.33| 
 | es | Bloom | 18.76|32.70|--|24.80|20.92| 
 | es | M2M | 12.11|25.09|--|29.33|14.86| 
 | fr | Bloom | 23.44|45.59|27.51|--|23.15| 
 | fr | M2M | 15.36|37.17|25.60|--|17.61| 
 | zh | Bloom | 15.05|30.50|20.54|26.01|--| 
 | zh | M2M | 11.55|20.91|16.92|24.32|--| 
