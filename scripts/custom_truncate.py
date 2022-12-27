#!/usr/bin/python
import re
import sys

for line in sys.stdin:
    src, ref, pred = line.strip('\n').split('\t')
    pred = re.sub('([\.=] .+?: .+?)$', '', pred)
    print('\t'.join([src, ref, pred.strip()]))
