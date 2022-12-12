#!/usr/bin/python
import random
random.seed(42)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('example_file')
parser.add_argument('number_examples', type=int)
args = parser.parse_args()

contents = []
with open(args.example_file) as fp:
    for line in fp:
        contents.append(line.strip())

random_lines = random.sample(range(len(contents)), k=args.number_examples)

for random_line in random_lines:
    print(contents[random_line])


