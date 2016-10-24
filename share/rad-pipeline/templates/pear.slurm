{slurmheader}

###
# Author:      Andrew Robinson
# Date:        2014-12-10
# Description: Uses pear to combine overlapping paired-end sequences
###

# Command used to generate this file:
# {CMD}

## SETTINGS ##

# add your pear options here
OPTS=""

FILES="{files}"

CORES={cores}

## End SETTINGS ##


# load modules
module load pear-gcc/{pearversion}  rad-pipeline/{radpipelineversion}

rad_job_log Starting $0

# pair each input file
# loops over each R1 filtered file
MD5="MD5 Hashes:"
for SRCFILENAME1 in `ls -1 ${{FILES}}`; do
        echo "Running: $SRCFILENAME1 at: " `date`
        OUTFILE=`basename $SRCFILENAME1 | sed 's/_R1_/_/g'`;
        OUTFILE="${{OUTFILE%%.*}}_paired"

        # compute the pair filename
        # replaces '_R1_' with '_R2_' so may break if you named your files differently
        SRCFILENAME2=`echo $SRCFILENAME1 | sed 's/_R1_/_R2_/g'`
        echo "Pair:    $SRCFILENAME2"

        CMD="pear -j $CORES $OPTS -o $OUTFILE -f $SRCFILENAME1 -r $SRCFILENAME2"
        echo $CMD
        $CMD

        # merge assembled and forward
	CMD="cat $OUTFILE.assembled.fastq $OUTFILE.unassembled.forward.fastq"
	echo "$CMD > $OUTFILE.mergeforward.fastq"
	$CMD > $OUTFILE.mergeforward.fastq

        # compute md5 hash
        echo "md5sum $OUTFILE.assembled.fastq"
        MD5="$MD5\n`md5sum $OUTFILE.assembled.fastq`"
        echo "md5sum $OUTFILE.discarded.fastq"
        MD5="$MD5\n`md5sum $OUTFILE.discarded.fastq`"
        echo "md5sum $OUTFILE.unassembled.forward.fastq"
        MD5="$MD5\n`md5sum $OUTFILE.unassembled.forward.fastq`"
        echo "md5sum $OUTFILE.unassembled.reverse.fastq"
        MD5="$MD5\n`md5sum $OUTFILE.unassembled.reverse.fastq`"
        echo "md5sum $OUTFILE.mergeforward.fastq"
        MD5="$MD5\n`md5sum $OUTFILE.mergeforward.fastq`"
done

# print details of output files (provenance)
echo -e "\nDirectory Contents:"
ls -l
echo ""
echo -e $MD5
echo ""

rad_job_log Finished $0

