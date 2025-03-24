
for folder in $2/* ; do
    filepath=$1/p2_cranfield_$(basename $folder).txt
    echo "qrels	algorithm	measure	user_id	score" > $filepath
    for q in data/*interest*.qrels
    do
        for f in $folder/*.results ; do
            python ../research/Compatibility/compatibility.py $q $f | gawk -F '\t' '{print "'`basename $q .qrels`'\t'`basename $f .results`'\t"$1"-95\t"$2"\t"$3}' ;
        done >> $filepath

        for f in $folder/*.results ; do
            python ../research/Compatibility/compatibility.py -p 0.98 $q $f | gawk -F '\t' '{print "'`basename $q .qrels`'\t'`basename $f .results`'\t"$1"-98\t"$2"\t"$3}' ;
        done >> $filepath
    done
done

# Example usage from root directory:
# scripts/evaluation/calculate_compatibility.sh results/metrics/compatibility results/runs_reranked
