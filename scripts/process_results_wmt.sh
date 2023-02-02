#!/bin/bash

scriptdir=`dirname $0`
outputdir=`realpath $scriptdir/../outputs`
dataset=wmt14-fr-en
shot_num=5

# extract tsv from json
echo ">> Extracting tsv from jsonl"
OIFS="$IFS"
IFS=$'\n'
for jsonfile in `find $outputdir/$dataset/$shot_num-shot/jsonl -type f -name examples.*.jsonl`; do
    # basic output
    output=`basename ${jsonfile%.jsonl}.tsv`;
    echo "Producing $output"
    python $scriptdir/jsonl_to_tsv.py "$jsonfile" "$outputdir/$dataset/$shot_num-shot/tsv/$output";
    # cut on first newline
    output=`basename ${jsonfile%.jsonl}.newline-cut.tsv`;
    echo "Producing $output"
    python $scriptdir/jsonl_to_tsv.py -n "$jsonfile" "$outputdir/$dataset/$shot_num-shot/tsv/$output";
    # also do custom truncation to avoid repeating translations
    new_output="$outputdir/$dataset/$shot_num-shot/tsv/${output%.tsv}-custom-truncate.tsv"
    cat "$outputdir/$dataset/$shot_num-shot/tsv/$output" | python $scriptdir/custom_truncate.py > "$new_output"
done


# evaluate with BLEU and COMET (do not rewrite COMET each time as results take a while to recalculate)
echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tspBLEU" > $outputdir/$dataset/$shot_num-shot/bleu-results.tsv
if [ ! -f $outputdir/$dataset/$shot_num-shot/comet-results.tsv ]; then
    echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tcomet" > $outputdir/$dataset/$shot_num-shot/comet-results.tsv
fi
for tsvfile in `ls -1 $outputdir/$dataset/$shot_num-shot/tsv/examples.*.tsv | sort`; do
    filename=`basename $tsvfile`
    model=`echo $tsvfile | perl -pe 's/.+?model=(.+?)\.task.+?$/\1/'`
    task=`echo $tsvfile | perl -pe 's/.+?task=(.+?)\.templates.+?$/\1/'`
    templates=`echo $tsvfile | perl -pe 's/.+?templates=(.+?)\.fewshot.+?$/\1/'`
    fewshot=`echo $tsvfile | perl -pe 's/.+?fewshot=(.+?)\.(seed|batchsize).+?$/\1/'`
    seed=`echo $tsvfile | perl -pe 's/.+?seed=(.+?)\.timestamp.+?$/\1/'`
    timestamp=`echo $tsvfile | perl -pe 's/.+?timestamp=(.+?)\..+?$/\1/'`
    postproc=`echo $tsvfile | perl -pe 's/.+?timestamp=.+?\.(.*?)\.?tsv/\1/'`
    
    if ! grep -q "$filename" "$outputdir/$dataset/$shot_num-shot/bleu-results.tsv"; then
	bleu=`sacrebleu -w2 -b -tok 13a <(cat "$tsvfile" | cut -f2) < <(cat "$tsvfile" | cut -f3)`
	echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$bleu\t" >> $outputdir/$dataset/$shot_num-shot/bleu-results.tsv
    fi
    if ! grep -q $filename $outputdir/$dataset/$shot_num-shot/comet-results.tsv; then
	#comet=`comet-score -s <(cat "$tsvfile" | cut -f1 | perl -pe 's/^.*?### ([A-Z][\-a-z ]+?): *(.+?) *= ([A-Z][a-z]+?]):$/\2/') \
        #  -r <(cat "$tsvfile" | cut -f2) -t <(cat "$tsvfile" | cut -f3) --quiet`		     
	#echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$comet\t" >> $outputdir/$dataset/$shot_num-shot/comet-results.tsv
	echo
    fi
done
IFS="$OIFS"
