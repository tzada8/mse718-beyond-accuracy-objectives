echo "qrels	algorithm	measure	user_id	score" > $1

for q in data/*interest*.qrels
do

    for f in $2/*.results ; do python ../research/Compatibility/compatibility.py $q $f | gawk -F '\t' '{print "'`basename $q .qrels`'\t'`basename $f .results`'\t"$1"-95\t"$2"\t"$3}' ; done >> $1

    for f in $2/*.results ; do python ../research/Compatibility/compatibility.py -p 0.98 $q $f | gawk -F '\t' '{print "'`basename $q .qrels`'\t'`basename $f .results`'\t"$1"-98\t"$2"\t"$3}' ; done >> $1

done

# Example usage from root directory:
# scripts/evaluation/calculate-compatibility.sh results/metrics/p2-cranfield.txt data/runs
