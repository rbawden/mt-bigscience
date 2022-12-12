# MT@BigScience

Evaluation results for Machine Translation within the BigScience project

## Outputs and evaluation


### Extract predictions
The raw outputs are in `outputs/{diabla,flores101,wmt-14}/{0,1}-shot/jsonl`.

To extract the text (context, reference, prediction): 
```
python scripts/jsonl_to_tsv.py <JSONL_FILE> <OUTPUT_TSV_FILE>
```

### Evaluate predictions

To evaluate all DiaBLa predictions:
```
python scripts/get_all_diabla_results.py outputs/diabla/
```
