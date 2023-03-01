# MT@BigScience

Evaluation results for Machine Translation within the BigScience project

## Citation

This repository contains codes and outputs to accompany the paper ``Investigating the Translation Performance of a Large Multilingual
Language Model: the Case of BLOOM''. Please cite the following:

```
@misc{bloom-eval-2023
TBD
}
```

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


## Results (BLEU scores)

### Cross-dataset and model comparison (focus on English-French and English-Hindi)

WMT14 results (Original outputs)
Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |
|---|---|---|---|---|---|
| en→fr | 0 | 14.91 | 1.21 | 29.27 | 12.95 |
| | 1 | 27.83 | 1.41 | 25.24 | 21.92 |
| fr→en | 0 | 15.52 | 25.79 | 32.88 | 15.54 |
| | 1 | 34.61 | 21.01 | 30.03 | 24.55 |
| en→hi | 0 | 6.80 | 0.16 | 11.20 | 0.14 |
| | 1 | 13.62 | 0.12 | 9.50 | 0.08 |
| hi→en | 0 | 12.05 | 0.00 | 26.13 | 0.42 |
| | 1 | 25.04 | 0.01 | 20.15 | 0.58 |

DiaBLa results (Original outputs)
Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |
|---|---|---|---|---|---|
| en→fr | 0 | 0.88 | 0.52 | 28.44 | 0.53 |
| | 1 | 5.70 | 0.61 | 21.03 | 15.52 |
| fr→en | 0 | 0.85 | 25.51 | 34.96 | 0.83 |
| | 1 | 12.05 | 20.57 | 26.88 | 12.05 |

Flores-101 results (Original outputs)
Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |
|---|---|---|---|---|---|
| en→fr | 0 | 2.77 | 1.86 | 55.45 | 2.76 |
| | 1 | 44.99 | 2.13 | 53.53 | 24.36 |
| fr→en | 0 | 2.73 | 31.90 | 0.00 | 2.59 |
| | 1 | 45.59 | 24.86 | 58.22 | 16.74 |
| en→hi | 0 | 1.29 | 0.15 | 67.69 | 0.07 |
| | 1 | 27.25 | 0.06 | 54.66 | 0.12 |
| hi→en | 0 | 3.40 | 0.00 | 59.55 | 0.10 |
|  | 1 | 35.06 | 0.19 | 57.32 | 0.45 |

WMT14 results (Truncated outputs)
Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |
|---|---|---|---|---|---|
| en→fr | 0 | 32.25 | 1.21 | 29.24 | 18.86 |
| | 1 | 36.29 | 1.41 | 25.19 | 22.31 |
| fr→en | 0 | 37.16 | 25.80 | 32.87 | 33.18 |
| | 1 | 38.18 | 21.07 | 29.95 | 33.25 |
| en→hi | 0 | 12.10 | 0.16 | 11.20 | 0.11 |
| | 1 | 15.73 | 0.12 | 9.50 | 0.08 |
| hi→en | 0 | 24.29 | 0.00 | 26.06 | 0.51 |
| | 1 | 25.04 | 0.01 | 20.06 | 0.61 |

DiaBLa results (Truncated outputs)
Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |
|---|---|---|---|---|---|
| en→fr | 0 | 24.23 | 0.52 | 28.44 | 17.42 |
| | 1 | 37.57 | 0.61 | 21.89 | 20.71 |
| fr→en | 0 | 22.94 | 25.51 | 34.92 | 36.80 |
| | 1 | 41.36 | 21.09 | 27.20 | 37.63 |

Flores-101 results (Truncated outputs)
Lang. dir | #shots | BLOOM | T0 | mT0-xxl | OPT |
|---|---|---|---|---|---|
| en→fr | 0 | 26.91 | 1.85 | 55.34 | 21.40 |
| | 1 | 49.32 | 2.13 | 53.40 | 28.41 |
| fr→en | 0 | 40.28 | 31.90 | 0.00 | 39.41 |
| | 1 | 47.24 | 25.20 | 58.24 | 39.82 |
| en→hi | 0 | 7.74 | 0.15 | 67.69 | 0.12 |
| | 1 | 29.52 | 0.06 | 54.66 | 0.12 |
| hi→en | 0 | 30.19 | 0.00 | 59.55 | 0.23 |
|  | 1 | 35.06 | 0.19 | 57.27 | 0.50 |

### Flores-101: High-resource, 1-shot
(Original outputs with no postprocessing)

| Src↓ | Trg→ | ar | en | es | fr | zh |
|---|---|---|---|---|---|---|
 | ar | Bloom | -- | 40.28 | 23.32 | 33.12 | 17.68 |
 |  | M2M | -- | 25.50 | 16.74 | 25.69 | 13.10 |
 | en | Bloom | 28.21 | -- | 29.42 | 44.99 | 26.69 |
 |  | M2M | 17.92 | -- | 25.57 | 41.99 | 19.33 |
 | es | Bloom | 18.76 | 32.70 | -- | 24.80 | 20.92 |
 |  | M2M | 12.11 | 25.09 | -- | 29.33 | 14.86 |
 | fr | Bloom | 23.44 | 45.59 | 27.51 | -- | 23.15 |
 |  | M2M | 15.36 | 37.17 | 25.60 | -- | 17.61 |
 | zh | Bloom | 15.05 | 30.50 | 20.54 | 26.01 | -- |
 |  | M2M | 11.55 | 20.91 | 16.92 | 24.32 | -- |

### Flores-101:High-mid resource, 1-shot
(Original outputs with no postprocessing)

| Src↓ | Trg→ | en | fr | hi | id | vi |
|---|---|---|---|---|---|---|
 | en | Bloom | -- | 44.99 | 27.25 | 39.00 | 28.54 |
 |  | M2M | -- | 41.99 | 28.15 | 37.26 | 35.10 |
 | fr | Bloom | 45.59 | -- | 18.47 | 31.44 | 32.76 |
 |  | M2M | 37.17 | -- | 22.91 | 29.14 | 30.26 |
 | hi | Bloom | 35.06 | 27.62 | -- | -- | -- |
 |  | M2M | 27.89 | 25.88 | -- | -- | -- |
 | id | Bloom | 43.25 | 30.35 | -- | -- | -- |
 |  | M2M | 33.74 | 30.81 | -- | -- | -- |
 | vi | Bloom | 38.71 | 26.85 | -- | -- | -- |
 |  | M2M | 29.51 | 25.82 | -- | -- | -- |
 
 ### Flores-101: Low-resource, 1-shot
 (Original outputs with no postprocessing)
 
| Src↓ | Trg→ | bn | en | hi | sw | yo |
|---|---|---|---|---|---|---|
 | en | Bloom | -- | 24.65 | 27.25 | 20.51 | 2.60 |
 |  | M2M | -- | 23.04 | 28.15 | 26.95 | 2.17 |
 | bn | Bloom | 29.91 | -- | 16.34 | -- | -- |
 |  | M2M | 22.86 | -- | 21.76 | -- | -- |
 | hi | Bloom | 35.06 | 23.77 | -- | -- | -- |
 |  | M2M | 27.89 | 21.77 | -- | -- | -- |
 | sw | Bloom | 37.40 | -- | -- | -- | 1.31 |
 |  | M2M | 30.43 | -- | -- | -- | 1.29 |
 | yo | Bloom | 4.08 | -- | -- | 0.89 | -- |
 |  | M2M | 4.18 | -- | -- | 1.93 | -- | 
 
 ### Flores-101: Romance languages, 1-shot
 (Original outputs with no postprocessing)
 
 | Src↓ | Trg→ | ca | es | fr | gl | it | pt|
|---|---|---|---|---|---|---|---|
 | ca | Bloom | -- | 28.92 | 33.79 | 19.24 | 19.85 | 33.05 | 
 |  | M2M | -- | 25.17 | 35.08 | 33.42 | 25.50 | 35.17 | 
 | es | Bloom | 31.16 | -- | 24.80 | 23.28 | 16.49 | 29.11 | 
 |  | M2M | 23.12 | -- | 29.33 | 27.54 | 23.87 | 28.10 | 
 | fr | Bloom | 37.16 | 27.51 | -- | 24.92 | 23.97 | 38.94 | 
 |  | M2M | 28.74 | 25.60 | -- | 32.82 | 28.56 | 37.84 | 
 | gl | Bloom | 37.49 | 27.09 | 33.77 | -- | 18.26 | 32.16 | 
 |  | M2M | 30.07 | 27.65 | 37.06 | -- | 26.87 | 34.81 | 
 | it | Bloom | 31.00 | 25.40 | 31.36 | 20.16 | -- | 29.15 | 
 |  | M2M | 25.20 | 29.23 | 34.39 | 29.23 | -- | 31.47 | 
 | pt | Bloom | 39.56 | 28.07 | 40.34 | 27.10 | 20.06 | -- | 
 |  | M2M | 30.69 | 26.88 | 40.17 | 33.77 | 28.09 | -- | 
 
 
 ### Flores-101: Bengali→English MT, Transfer using 1-shot example from a different language direction
  (Original outputs with no postprocessing)
  

| 1-shot example direction type | 1-shot example direction | spBLEU orig. | COMET orig. | spBLEU trunc. | COMET trunc. |
|---|---|---|---|---|---|
| Same | bn→en | 29.91 | 0.4440 | 29.91 | 0.4440 |
| Opposite | en→bn | 21.81 | 0.3132 | 29.42 | 0.4143 |
| Related source | hi→en | 30.14 | 0.4492 | 30.54 | 0.4603 |
| Related source (from WMT) | hi→en | 29.06 | 0.4216 | 29.07 | 0.4274 |
| HR unrelated source | fr→en | 17.19 | 0.3147 | 29.68 | 0.3960 |
| HR unrelated source | fr→ar | 8.44 | -0.1025 | 27.99 | 0.3218 |

### DiaBLa context results (1-shot with differing source of context)

The 1-shot example can be:
- from either anywhere in the document (Origin=Rand.) or the previous sentence (Origin=Prev.)
- from any language direction (en→fr or fr→en) regardless of the language direction of the current example (Direction=rand.), from the same direction as the current example (Direction=same) or the opposite direction (Direction=opposite).

| Origin | Direction | Truncate | en→fr BLEU | en→fr COMET | fr→en BLEU | fr→en COMET |
|---|---|---|---|---|---|---|
| Rand. | rand. | ❌ | 5.70 | 0.3421 | 12.05 | 0.6138 |
| | | ✅ | 37.57 | 0.6343 | 41.36 | 0.7576 |
| Prev. | rand. | ❌ | 6.10 | 0.3280 | 12.34 | 0.6166 |
| | | ✅ | 38.51 | 0.6139 | 41.57 | 0.7513 |
| Prev. | Same | ❌ | 19.32 | 0.5965 | 20.71 | 0.7190 |
| | | ✅ | 38.95 | 0.6325 | 42.10 | 0.7607 |
| Prev. | Opposite | ❌ | 3.64 | 0.0635 | 8.56 | 0.5184 |
| | | ✅ | 37.76 | 0.5898 | 41.20 | 0.7423 |
