#!/bin/sh

scriptdir=`dirname $0`
outputdir=`realpath $scriptdir/../outputs`
dataset=flores-101

# extract tsv from jsonl
echo ">> Extracting tsv from jsonl"
OIFS="$IFS"
IFS=$'\n'
for jsonfile in `find $outputdir/$dataset/1-shot/jsonl -type f -name examples.*`; do
    # basic output
    output=`basename ${jsonfile%.jsonl}.tsv`;
    echo "Producing $output"
    python $scriptdir/jsonl_to_tsv.py "$jsonfile" "$outputdir/$dataset/1-shot/tsv/$output";
    # cut on first newline
    output=`basename ${jsonfile%.jsonl}.newline-cut.tsv`;
    echo "Producing $output"
    python $scriptdir/jsonl_to_tsv.py -n "$jsonfile" "$outputdir/$dataset/1-shot/tsv/$output";
    # also do custom truncation to avoid repeating translations
    new_output="$outputdir/$dataset/1-shot/tsv/${output%.tsv}-custom-truncate.tsv"
    cat "$outputdir/$dataset/1-shot/tsv/$output" | python $scriptdir/custom_truncate.py > "$new_output"
done


# evaluate with BLEU
for tsvfile in `ls -1 $outputdir/$dataset/1-shot/tsv/examples.* | sort`; do
    filename=`basename $tsvfile`
    if ! grep -q "$filename" "$outputdir/$dataset/1-shot/bleu-results.tsv"; then
	bleu=`sacrebleu -w2 -b -tok flores101 <(cat "$tsvfile" | cut -f2) < <(cat "$tsvfile" | cut -f3)`
	echo -e "$filename\t$bleu" >> $outputdir/$dataset/1-shot/bleu-results.tsv
    fi
    if ! grep -q $filename $outputdir/$dataset/1-shot/comet-results.tsv; then
	comet=`comet-score -s <(cat "$tsvfile" | cut -f1 | perl -pe 's/^.*?### ([A-Z][\-a-z ]+?): *(.+?) *= ([A-Z][a-z]+?]):$/\2/') \
    -r <(cat "$tsvfile" | cut -f2) -t <(cat "$tsvfile" | cut -f3) --quiet`		     
	echo -e "$filename\t$comet" >> $outputdir/$dataset/1-shot/comet-results.tsv
    fi
    
done
IFS="$OIFS"
