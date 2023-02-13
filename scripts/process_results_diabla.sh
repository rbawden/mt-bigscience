#!/bin/sh

scriptdir=`dirname $0`
outputdir=`realpath $scriptdir/../outputs`

for shot_num in 0 1; do
    # separate language directions
    echo ">> Separating language directions"
    for jsonfile in `ls $outputdir/diabla/$shot_num-shot/jsonl/examples.* | grep -v "English.jsonl" | grep -v "French.jsonl"`; do
	for langdir in English-French French-English; do
	    src=`echo $langdir | cut -f1 -d"-"`
	    output=${jsonfile%.jsonl}.$langdir.jsonl
	    if [ ! -f $output ]; then
		python $scriptdir/get_langdir_docids.py $jsonfile $src > $output
		echo "Producing $output"
	    fi
	done
    done
    
    # extract tsv from jsonl
    echo ">> Extracting tsv from jsonl"
    for jsonfile in $outputdir/diabla/$shot_num-shot/jsonl/examples.*; do
	# basic output
	output=`basename ${jsonfile%.jsonl}.tsv`;
	if [ ! -f "$outputdir/diabla/$shot_num-shot/tsv/$output" ]; then
	    echo "Producing $output"
	    python $scriptdir/jsonl_to_tsv.py $jsonfile "$outputdir/diabla/$shot_num-shot/tsv/$output"
	fi
	# cut on first newline
	output=`basename ${jsonfile%.jsonl}.newline-cut.tsv`;
	if [ ! -f "$outputdir/diabla/$shot_num-shot/tsv/$output" ]; then
	    python $scriptdir/jsonl_to_tsv.py -n $jsonfile $outputdir/diabla/$shot_num-shot/tsv/$output;
	fi
	# also do custom truncation to avoid repeating translations
	new_output=$outputdir/diabla/$shot_num-shot/tsv/${output%.tsv}-custom-truncate.tsv
	if [ ! -f "$new_output" ]; then
	    cat $outputdir/diabla/$shot_num-shot/tsv/$output | python $scriptdir/custom_truncate.py > "$new_output"
	fi
    done
    
    # evaluate with BLEU and COMET (do not rewrite results each time as they can take a while to recalculate)
    if [ ! -f $outputdir/$dataset/$shot_num-shot/bleu-results.English-French.tsv ]; then
	echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tspBLEU" > $outputdir/$dataset/$shot_num-shot/bleu-results.English-French.tsv
    fi
    if [ ! -f $outputdir/$dataset/$shot_num-shot/comet-results.English-French.tsv ]; then
	echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tcomet" > $outputdir/$dataset/$shot_num-shot/comet-results.English-French.tsv
    fi
    
    # evaluate with BLEU and COMET
    for tsvfile in `ls $outputdir/diabla/$shot_num-shot/tsv/examples.*English-French* | sort`; do
	filename=`basename $tsvfile`
	model=`echo $tsvfile | perl -pe 's/.+?model=(.+?)\.task.+?$/\1/'`
	task=`echo $tsvfile | perl -pe 's/.+?task=(.+?)\.templates.+?$/\1/'`
	templates=`echo $tsvfile | perl -pe 's/.+?templates=(.+?)\.fewshot.+?$/\1/'`
	fewshot=`echo $tsvfile | perl -pe 's/.+?fewshot=(.+?)\.seed.+?$/\1/'`
	seed=`echo $tsvfile | perl -pe 's/.+?seed=(.+?)\.timestamp.+?$/\1/'`
	timestamp=`echo $tsvfile | perl -pe 's/.+?timestamp=(.+?)\..+?$/\1/'`
	postproc=`echo $tsvfile | perl -pe 's/.+?timestamp=.+?\.English-French\.(.*?)\.?tsv/\1/'`
	if ! grep -Fq "$filename" "$outputdir/diabla/$shot_num-shot/bleu-results.English-French.tsv"; then
	    bleu=`sacrebleu -w2 -b <(cat $tsvfile | cut -f2) < <(cat $tsvfile | cut -f3)`
	    echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$bleu\t" >> $outputdir/diabla/$shot_num-shot/bleu-results.English-French.tsv
	fi
	#    if ! grep -Fq "$filename" "$outputdir/diabla/$shot_num-shot/comet-results.English-French.tsv"; then
	#	comet=`comet-score --batch_size 8 -s <(cat $tsvfile | cut -f1 | perl -pe 's/^.*?### (English|French): *(.+?) *= (English|French):$/\2/') \
	    #	    -r <(cat $tsvfile | cut -f2) -t <(cat $tsvfile | cut -f3) --quiet`
	#    echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$comet >> $outputdir/diabla/$shot_num-shot/comet-results.English-French.tsv
	#	echo
	#   fi
	
    done
    
    if [ ! -f $outputdir/$dataset/$shot_num-shot/bleu-results.French-English.tsv ]; then
	echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tspBLEU" > $outputdir/$dataset/$shot_num-shot/bleu-results.French-English.tsv
    fi
    if [ ! -f $outputdir/$dataset/$shot_num-shot/comet-results.French-English.tsv ]; then
	echo -e "model\ttask\ttemplate\tfewshot\tseed\tpostproc\ttimestamp\tfilename\tcomet" > $outputdir/$dataset/$shot_num-shot/comet-results.French-English.tsv
    fi
    
    for tsvfile in `ls $outputdir/diabla/$shot_num-shot/tsv/examples.*French-English* | sort`; do
	filename=`basename $tsvfile`
	model=`echo $tsvfile | perl -pe 's/.+?model=(.+?)\.task.+?$/\1/'`
	task=`echo $tsvfile | perl -pe 's/.+?task=(.+?)\.templates.+?$/\1/'`
	templates=`echo $tsvfile | perl -pe 's/.+?templates=(.+?)\.fewshot.+?$/\1/'`
	fewshot=`echo $tsvfile | perl -pe 's/.+?fewshot=(.+?)\.seed.+?$/\1/'`
	seed=`echo $tsvfile | perl -pe 's/.+?seed=(.+?)\.timestamp.+?$/\1/'`
	timestamp=`echo $tsvfile | perl -pe 's/.+?timestamp=(.+?)\..+?$/\1/'`
	postproc=`echo $tsvfile | perl -pe 's/.+?timestamp=.+?\.French-English\.(.*?)\.?tsv/\1/'`
	if ! grep -Fq "$filename" "$outputdir/diabla/$shot_num-shot/bleu-results.French-English.tsv"; then
	    bleu=`sacrebleu -w2 -b <(cat $tsvfile | cut -f2) < <(cat $tsvfile | cut -f3)`
	    echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$bleu\t" >> $outputdir/diabla/$shot_num-shot/bleu-results.French-English.tsv
	fi
	#if ! grep -Fq "$filename" "$outputdir/diabla/$shot_num-shot/comet-results.French-English.tsv"; then
	#	comet=`comet-score --batch_size 8 -s <(cat $tsvfile | cut -f1 | perl -pe 's/^.*?### (English|French): *(.+?) *= (English|French):$/\2/') \
	    #	    -r <(cat $tsvfile | cut -f2) -t <(cat $tsvfile | cut -f3) --quiet`
	#    echo -e "$model\t$task\t$templates\t$fewshot\t$seed\t$postproc\t$timestamp\t$filename\t$comet >> $outputdir/diabla/$shot_num-shot/comet-results.French-English.tsv 
	#   fi
	
    done
done
