{slurmheader}

###
# Author:      Andrew Robinson
# Date:        2014-12-08
# Description: Uses seq-sets to compute the union of all contaminated sequences and
#              then filters the raw sequences to remove contamination.
###

# Command used to generate this file:
# {CMD}

# load modules
module load biostreamtools-gcc/{biostreamtoolsversion} parallel/{parallelversion}  rad-pipeline/{radpipelineversion}

rad-pipeline_log Starting $0

# filter each input file
MD5="MD5 Hashes:"
for SRCFILENAME in {rawfiles}; do
        echo "Running: $SRCFILENAME at: " `date`
        OUTFILE=`basename $SRCFILENAME`;
        OUTFILE="${{OUTFILE%%.*}}_filtered.fastq"

        CMD="seq-sets --mode NOTUNION -o $OUTFILE -s $SRCFILENAME {krakenfiles}"
        echo $CMD
        $CMD

        # compute md5 hash
        echo "md5sum $OUTFILE"
        MD5="$MD5\n`md5sum $OUTFILE`"
done

# print details of output files (provenance)
echo -e "\nDirectory Contents:"
ls -l
echo ""
echo -e $MD5
echo ""

rad-pipeline_log Finished $

