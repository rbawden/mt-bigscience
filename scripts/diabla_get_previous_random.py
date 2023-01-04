#!/usr/bin/python
import json
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('random_one_shot')
parser.add_argument('prev_one_shot_same')
parser.add_argument('prev_one_shot_opposite')
args = parser.parse_args()

def read_jsonl(filename):
    examples = {}
    with open(filename) as fp:
        for line in fp:
            example = json.loads(line)
            examples[example['doc_id']] = example
    return examples

random = read_jsonl(args.random_one_shot)
prev_same = read_jsonl(args.prev_one_shot_same)
prev_opposite = read_jsonl(args.prev_one_shot_opposite)

for docid in random:
    rand_ex = random[docid]
    few_shot_src_lang = rand_ex['ctx'].split(':')[0]
    current_src_lang = re.match('^.*?\n###\n(French|English)', rand_ex['ctx']).group(1)

    if few_shot_src_lang == current_src_lang:
        chosen = prev_same[docid]
    else:
        chosen = prev_opposite[docid]

    print(json.dumps(chosen))
