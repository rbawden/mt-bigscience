#!/bin/sh

scriptdir=`dirname $0`
outputdir=`realpath $scriptdir/../outputs`
dataset=flores-101

for shot_num in 0 1; do
    # extract tsv from jsonl
    echo ">> Extracting tsv from jsonl"
    OIFS="$IFS"
    IFS=$'\n'
    for jsonfile in `find $outputdir/$dataset/$shot_num-shot/jsonl -type f -name examples.*`; do
	# basic output
	output=`basename ${jsonfile%.jsonl}.tsv`;
	if [ ! -f "$outputdir/$dataset/$shot_num-shot/tsv/$output" ]; then
	    echo "Producing $output"
	    python $scriptdir/jsonl_to_tsv.py "$jsonfile" "$outputdir/$dataset/$shot_num-shot/tsv/$output";
	fi
	# cut on first newline
	output=`basename ${jsonfile%.jsonl}.newline-cut.tsv`;
	if [ ! -f "$outputdir/$dataset/$shot_num-shot/tsv/$output" ]; then
	    python $scriptdir/jsonl_to_tsv.py -n "$jsonfile" "$outputdir/$dataset/$shot_num-shot/tsv/$output";
	fi
	new_output="$outputdir/$dataset/$shot_num-shot/tsv/${output%.tsv}-custom-truncate.tsv"
	# also do custom truncation to avoid repeating translations
	if [ ! -f "$new_output" ]; then
	    cat "$outputdir/$dataset/$shot_num-shot/tsv/$output" | python $scriptdir/custom_truncate.py > "$new_output"
	fi
    done
    
    
    # evaluate with BLEU and COMET (do not rewrite COMET each time as results take a while to recalculate)
    if [ ! -f $outputdir/$dataset/$shot_num-shot/bleu-results.tsv ]; then
	echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tspBLEU" > $outputdir/$dataset/$shot_num-shot/bleu-results.tsv
    fi
    if [ ! -f $outputdir/$dataset/$shot_num-shot/comet-results.tsv ]; then
	echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tcomet" > $outputdir/$dataset/$shot_num-shot/comet-results.tsv
    fi
    for tsvfile in `ls -1 $outputdir/$dataset/$shot_num-shot/tsv/examples.* | sort`; do
	filename=`basename $tsvfile`
	model=`echo $tsvfile | perl -pe 's/.+?model=(.+?)\.task.+?$/\1/'`
	task=`echo $tsvfile | perl -pe 's/.+?task=(.+?)\.templates.+?$/\1/'`
	templates=`echo $tsvfile | perl -pe 's/.+?templates=(.+?)\.fewshot.+?$/\1/'`
	fewshot=`echo $tsvfile | perl -pe 's/.+?fewshot=(.+?)\.seed.+?$/\1/'`
	seed=`echo $tsvfile | perl -pe 's/.+?seed=(.+?)\.timestamp.+?$/\1/'`
	timestamp=`echo $tsvfile | perl -pe 's/.+?timestamp=(.+?)\..+?$/\1/'`
	postproc=`echo $tsvfile | perl -pe 's/.+?timestamp=.+?\.(.*?)\.?tsv/\1/'`
	
	if ! grep -Fq "$filename" "$outputdir/$dataset/$shot_num-shot/bleu-results.tsv"; then
	    echo "Recalculating spBLEU for $filename"
	    bleu=`sacrebleu -w2 -b -tok flores101 <(cat "$tsvfile" | cut -f2) < <(cat "$tsvfile" | cut -f3)`
	    echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$bleu\t" >> $outputdir/$dataset/$shot_num-shot/bleu-results.tsv
	fi
	if ! grep -Fq "$filename" "$outputdir/$dataset/$shot_num-shot/comet-results.tsv"; then
	    comet=`comet-score --batch_size 8 -s <(cat "$tsvfile" | cut -f1 | perl -pe 's/^.*?### ([A-Z][\-a-z ]+?): *(.+?) *= ([A-Z][a-z]+?]):$/\2/') \
		  -r <(cat "$tsvfile" | cut -f2) -t <(cat "$tsvfile" | cut -f3) --quiet | perl -pe 's/^.+?score: ([\-0-9\.]+)/\1/'`
	    echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$comet\t" >> $outputdir/$dataset/$shot_num-shot/comet-results.tsv
	fi
    done
    IFS="$OIFS"
done
