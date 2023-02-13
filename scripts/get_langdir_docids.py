#!/usr/bin/python
import json
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('xglm_jsonl')
parser.add_argument('src_lang', choices=('English', 'French'))
args = parser.parse_args()

with open(args.xglm_jsonl) as fp:
    for line in fp:
        ex = json.loads(line)
        #if re.match('.+?###\n(English|French)', ex['ctx'], re.DOTALL).group(1) == args.src_lang:
        if re.match('.+?(English|French): *$', ex['ctx'], re.DOTALL).group(1) != args.src_lang:
            print(json.dumps(ex))
