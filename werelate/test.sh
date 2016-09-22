

bedtools intersect -header -c -a data/replication_timing.hg19.bed.gz -b data/cpgIsland.hg19.bed.gz | sort -k1,1 -k2,2n > bt
python werelate.py data/replication_timing.hg19.bed.gz data/cpgIsland.hg19.bed.gz | sort -k1,1 -k2,2n > we

mbt=$(md5sum bt | awk '{print $1}')
mwe=$(md5sum we | awk '{print $1}')

rm bt we

if [[ "$mbt" ==  "$mwe" ]]; then
    echo "SUCCESS" $mbt $mwe
else
    echo FAIL, $mbt, $mwe
fi

bedtools intersect -header -c -b data/replication_timing.hg19.bed.gz -a data/cpgIsland.hg19.bed.gz | grep -v ^# | sort -k1,1 -k2,2n > bt
python werelate.py data/cpgIsland.hg19.bed.gz data/replication_timing.hg19.bed.gz | sort -k1,1 -k2,2n > we

mbt=$(md5sum bt | awk '{print $1}')
mwe=$(md5sum we | awk '{print $1}')

rm bt we

if [[ "$mbt" ==  "$mwe" ]]; then
    echo "SUCCESS" $mbt $mwe
else
    echo FAIL $mbt $mwe
fi
