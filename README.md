# MT@BigScience

Evaluation results for Machine Translation within the BigScience project

## Outputs and evaluation

The raw outputs are in `outputs/{diabla,flores101,wmt-14}/{0,1}-shot/jsonl`.

To extract the text (context, reference, prediction): 
```
python scripts/jsonl_to_tsv.py <JSONL_FILE> <OUTPUT_TSV_FILE>
```

