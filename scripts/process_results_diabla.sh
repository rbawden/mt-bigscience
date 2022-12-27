#!/bin/sh

scriptdir=`dirname $0`
outputdir=`realpath $scriptdir/../outputs`

# separate language directions
echo ">> Separating language directions"
for jsonfile in `ls $outputdir/diabla/1-shot/jsonl/examples.* | grep -v "English.jsonl" | grep -v "French.jsonl"`; do
    for langdir in English-French French-English; do
	src=`echo $langdir | cut -f1 -d"-"`
	output=${jsonfile%.jsonl}.$langdir.jsonl
	python $scriptdir/get_langdir_docids.py $jsonfile $src > $output
	echo "Producing $output"
    done
done

# extract tsv from jsonl
echo ">> Extracting tsv from jsonl"
for jsonfile in $outputdir/diabla/1-shot/jsonl/examples.*; do
    # basic output
    output=`basename ${jsonfile%.jsonl}.tsv`;
    echo "Producing $output"
    python $scriptdir/jsonl_to_tsv.py $jsonfile $outputdir/diabla/1-shot/tsv/$output;
    # cut on first newline
    output=`basename ${jsonfile%.jsonl}.newline-cut.tsv`;
    echo "Producing $output"
    python $scriptdir/jsonl_to_tsv.py -n $jsonfile $outputdir/diabla/1-shot/tsv/$output;
    # also do custom truncation to avoid repeating translations
    new_output=$outputdir/diabla/1-shot/tsv/${output%.tsv}-custom-truncate.tsv
    cat $outputdir/diabla/1-shot/tsv/$output | python $scriptdir/custom_truncate.py > $new_output
done

rm $outputdir/diabla/1-shot/bleu-results.English-French.tsv $outputdir/diabla/1-shot/bleu-results.French-English.tsv
rm $outputdir/diabla/1-shot/comet-results.English-French.tsv $outputdir/diabla/1-shot/comet-results.French-English.tsv
# evaluate with BLEU
for tsvfile in `ls $outputdir/diabla/1-shot/tsv/examples.*English-French* | sort`; do
    bleu=`sacrebleu -w2 -b <(cat $tsvfile | cut -f2) < <(cat $tsvfile | cut -f3)`
    comet=`comet-score -s <(cat $tsvfile | cut -f1 | perl -pe 's/^.*?### (English|French): *(.+?) *= (English|French):$/\2/') \
    -r <(cat $tsvfile | cut -f2) -t <(cat $tsvfile | cut -f3) --gpus 0 --quiet`
    filename=`basename $tsvfile`
    echo -e "$filename\t$bleu" >> $outputdir/diabla/1-shot/bleu-results.English-French.tsv
    echo -e "$filename\t$comet" >> $outputdir/diabla/1-shot/comet-results.English-French.tsv
    
done
for tsvfile in `ls $outputdir/diabla/1-shot/tsv/examples.*French-English* | sort`; do
    bleu=`sacrebleu -w2 -b <(cat $tsvfile | cut -f2) < <(cat $tsvfile | cut -f3)`
    comet=`comet-score -s <(cat $tsvfile | cut -f1 | perl -pe 's/^.*?### (English|French): *(.+?) *= (English|French):$/\2/') \
    -r <(cat $tsvfile | cut -f2) -t <(cat $tsvfile | cut -f3) --gpus 0 --quiet`
    filename=`basename $tsvfile`
    echo -e "$filename\t$bleu" >> $outputdir/diabla/1-shot/bleu-results.French-English.tsv
    echo -e "$filename\t$comet" >> $outputdir/diabla/1-shot/comet-results.French-English.tsv
done
