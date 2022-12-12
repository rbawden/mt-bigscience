#!/usr/bin/python
import os
import json
import re


def protect(text, newline_cut=False):
    text = text.replace("\t", " ")
    if newline_cut:
        text = text.split("\n")[0]
    else:
        text = text.replace("\n", " ")
    return text


def extract_from_file(filename, newline_cut=False):
    content = []
    with open(filename) as fp:
        for line in fp:
            raw = json.loads(line)
            tsv = [
                protect(raw["ctx"], newline_cut),
                protect(raw["target"][0], newline_cut),
                protect(raw["pred"], newline_cut),
            ]
            content.append(tsv)
    return content


def write_to_tsv(outfile, content):
    with open(outfile, "w") as fp:
        for line in content:
            fp.write("\t".join(line) + "\n")


def extract_from_folder(infile, outfile, newline_cut=False):
    content = extract_from_file(infile, newline_cut=newline_cut)
    write_to_tsv(outfile, content)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl_file", help="Name of input filepath (jsonl format)")
    parser.add_argument("tsv_file", help="Name of output filepath (tsv format)")
    parser.add_argument(
        "-n",
        "--newline_end",
        help="cut at first newline",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    extract_from_folder(args.jsonl_file, args.tsv_file, args.newline_end)
