{slurmheader}

###
# Author:      Andrew Robinson
# Date:        2014-12-12
# Description: Demultiplexes RADtags (barcodes) using process_radtags (Stacks)
#              using all 48 barcodes.  After this it cleans un-used barcodes, 
#              merges forward/reverse reads and renames radtags into a user 
#              friendly filename.
# History:     This script is based on two scripts writen by Steve Doyle
#              called run_process_radtags and run_clean
###

# Command used to generate this file:
# {CMD}
# Date: {datetime}

## SETTINGS TO EDIT ##

# enzyme(s) used
#-e: provide the restriction enzyme used (cut site occurs on single-end read)
# "-e ENZ1"
# "--renz_1 ENZ1 --renz_2 ENZ2"
ENZYME="{enzymes}"

FILES="{files}"

# file to store read counts for each sample
READCOUNTFILE="sample.counts"

# Other flags to use
#-D: capture discarded reads to a file
#-q: discard reads with low quality scores
#-r: rescue barcodes and RAD-Tags
#-t: truncate final read length to this value
FLAGS="-D -q -r"
#FLAGS="-D -q -r -t 75"

## END SETTINGS ##

# load modules
module load stacks-gcc/{stacksversion} rad-pipeline/{radpipelineversion}

rad_job_log Starting $0

# get barcodes
BARCODES=$(cat ${{RAD_PIPELINE_DIR}}/share/rad-pipeline/ddRAD_barcodes)

# put header on count file
echo -e "Date:\t$(date)" >> $READCOUNTFILE
echo 'Filename	Barcode	Count' >> $READCOUNTFILE

# demultiplex each index one after another
MD5="MD5 Hashes:"
for R1FILENAME in `ls -1 $FILES`; do
        echo "Processing index: ${{R1FILENAME}} at:" `date`
        R2FILENAME=`echo $R1FILENAME | sed 's/_R1_/_R2_/g'`

	# check if files have read2 pair file
	INPUT_FILES="-f ${{R1FILENAME}}"
	PAIR=0
	if [ $R1FILENAME != $R2FILENAME ]; then
		if [ -e $R2FILENAME ]; then
			INPUT_FILES="-1 ${{R1FILENAME}} -2 ${{R2FILENAME}}"
			PAIR=1
		fi
	fi

	# check for gzipped files
	FILETYPE=$(ls -1 $R1FILENAME | awk '/.gz$/{{print "gzfastq"}} !/.gz$/{{print "fastq"}}')

        ## demultiplex radtags
	CMD="process_radtags ${{FLAGS}} ${{INPUT_FILES}} -o ./ -b ${{RAD_PIPELINE_DIR}}/data/ddRAD_barcodes ${{ENZYME}} -i ${{FILETYPE}}"
        echo $CMD
        $CMD

        ## clean up unused radtags
        INDEX=$(echo $R1FILENAME | sed 's/.*\(IDX[0-9][0-9]\).*/\1/g')

	# calculate the read count threshold
	# set to cutoff at 1/6 of reads spread over all 48 barcodes
	TOTAL_READ_COUNT=$(awk '/^Retained Reads/{{print $3}}' process_radtags.log )
	READ_THRESHOLD=$((TOTAL_READ_COUNT/288))

        # merge pairs and remove low count (unused) indices
        echo -e "\nRenaming samples for index: ${{INDEX}}"
	echo "Threshold: $READ_THRESHOLD reads"
        i=1
        for BARCODE in ${{BARCODES}}; do
		if [ $PAIR == 1 ]; then
                	MFILENAME="sample_${{BARCODE}}.1.fq"
                	MFILENAME="$MFILENAME sample_${{BARCODE}}.2.fq"

			# add remainder (singleton) files too
			# Uncomment if you want them included
			{norem}MFILENAME="$MFILENAME sample_${{BARCODE}}.rem.1.fq"
			{norem}MFILENAME="$MFILENAME sample_${{BARCODE}}.rem.2.fq"
		else
                	MFILENAME="sample_${{BARCODE}}.fq"
		fi

                II=`printf "%02d" $i`
                MERGEFILENAME="${{INDEX}}_RAD${{II}}.fq"

                # merge output files
                cat $MFILENAME > $MERGEFILENAME

                # remove low count indexes
                COUNT=$(wc -l $MERGEFILENAME | awk '{{ print $1}}')
		RCOUNT=$((COUNT/4))
                if [ $RCOUNT -lt $READ_THRESHOLD ] ; then
                        rm $MERGEFILENAME
                else
                        echo "${{BARCODE}} => ${{MERGEFILENAME}}"
			echo "${{MERGEFILENAME}}	${{BARCODE}}	${{RCOUNT}}" >> $READCOUNTFILE
                fi
                # increment i
                ((i++))
        done

        # remove forward/reverse (and singleton forward/reverse) read files
	rm sample_*.fq

        ## compute MD5 hashes of final files
        THISMD5=`md5sum ${{INDEX}}_RAD*`
        MD5="$MD5\n`echo $THISMD5 | perl -pe 's/(.*? .*?) /\1\\\\n/g'`"
done

# print details of output files (provenance)
echo -e "\nDirectory Contents:"
ls -l
echo ""
echo -e $MD5
echo ""

rad_job_log Finished $0

