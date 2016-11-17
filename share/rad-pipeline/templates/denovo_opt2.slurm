{slurmheader}
###
# Author:      Andrew Robinson
# Date:        2014-12-22
# Description: Optimised Stacks denovo_map.pl by varying parameters m, n and M
#              to allow the user to select the best combination.  This is stage
#              2 which covers every value near a target
###

# Command used to generate this file:
# {CMD}

module load stacks-gcc/{stacksversion} parallel/{parallelversion} rad-pipeline/{radpipelineversion}

rad-pipeline_log Starting $0

## SETTINGS TO EDIT ##

# options to try for -m
#-m: specify a minimum number of identical, raw reads required to create a stack
m_values=( {mvalues} )

# options to try for -n
#-n: specify the number of mismatches allowed between loci when building the catalog (default 0)
n_values=( {nvalues} )

# options to try for -M
#-M: specify the number of mismatches allowed between loci when processing a single individual (default 2)
M_values=( {Mvalues} )

# the number of threads to use for each denovo_map process
#NOTE: THREADS_PER_RUN * PARALLEL_JOBS must equal the number of CPU's you request in slurm
THREADS_PER_RUN="{corestask}"

# the number of denovo_map jobs to run in parallel
PARALLEL_JOBS="{paralleljobs}"

# other options
#-S: disable recording SQL data in the database.
#-t: remove, or break up, highly repetitive RAD-Tags in the ustacks program.
DENOVO_OPTS="{denovoopts}"

# batch id to use (by both denovo_map and populations)
BATCH_ID={batchid}

## END SETTINGS ##

## CHECK SETTINGS ##

# Do NOT edit this, use 'make_denovo_opt1_job' to set its value
INFILES="{files}"
#echo $INFILES

# check they specified a realistic number of test samples (2 to 4)
INFILES_COUNT=`ls -1 $INFILES | wc -l`
#if [ "$INFILES_COUNT" -gt 6 ]; then
#	echo "ERROR: you are trying to use way too many samples to optimise"
#	echo "       please select 2 to 4 representitives.  I am stopping!"
#	exit 1
#fi
if [ "$INFILES_COUNT" -gt 6 ] || [ "$INFILES_COUNT" -lt 2 ]; then
	echo "WARNING: sub-optimal number of samples.  I recommend you use"
	echo "         2 to 6 representitives.  I will let it pass this time"
fi

# check combinations
JOB_COUNT=`parallel --no-notice "echo \"\$PARALLEL_SEQ\"" ::: ${{M_values[*]}} ::: ${{n_values[*]}} ::: ${{m_values[*]}} | wc -l`
echo "Running: $JOB_COUNT jobs"
if [ "$JOB_COUNT" -gt 126 ]; then
	echo "WARNING: $JOB_COUNT jobs is going to take a long time to calculate."
	echo "         You should try to keep it under 126"
fi

# check CPU requirements
CPU_COUNT=$(($THREADS_PER_RUN * $PARALLEL_JOBS))
echo "On $CPU_COUNT cpus (${{PARALLEL_JOBS}}x ${{THREADS_PER_RUN}}cpus)"
if [ "$CPU_COUNT" -gt 16 ]; then
	echo "WARNING: $CPU_COUNT cpus is more than LIMS-HPC has on each node"
fi


## DO WORK ##

# make file options
INFILES_ARRAY=( $INFILES )
INFILES_WITH_S=${{INFILES_ARRAY[@]/#/-s }}

# make log directory
DENOVOLOG_DIR=denovolog2
{nocpdenovo}mkdir -p $DENOVOLOG_DIR

# make tmp directory
TMPDIR=/tmp/$USER/$SLURM_JOBID

mkdir -p $TMPDIR/stats

# command listing
CMD1="S=\$(date '+%s'); echo \"denovo_map with M={{1}} n={{2}} m={{3}}: starting\";"
CMD2="mkdir -p $TMPDIR/run_M{{1}}_n{{2}}_m{{3}};"
CMD3="denovo_map.pl $DENOVO_OPTS -T $THREADS_PER_RUN -M {{1}} -n {{2}} -m {{3}} -b 1 -D \"Optimise denovo_map.pl stage 1\" -o $TMPDIR/run_M{{1}}_n{{2}}_m{{3}}/ ${{INFILES_WITH_S}};"

#TODO: do populations part here
#CMD4="populations -b $BATCH_ID -P $TMPDIR/run_M{{1}}_n{{2}}_m{{3}} -M $POPMAP -t $THREADS_PER_RUN $POP_OPTS $OUTPUT_FORMATS;"

# collect stats
CMD5="collect_denovo_map_stats M{{1}}_n{{2}}_m{{3}} $TMPDIR/run_M{{1}}_n{{2}}_m{{3}}/denovo_map.log $INFILES >> $TMPDIR/stats/stats_M{{1}}_n{{2}}_m{{3}}.tsv;"
{nocpdenovo}CMD6="cp $TMPDIR/run_M{{1}}_n{{2}}_m{{3}}/denovo_map.log $DENOVOLOG_DIR/denovo_map_M{{1}}_n{{2}}_m{{3}}.log;"
CMD7="rm -r $TMPDIR/run_M{{1}}_n{{2}}_m{{3}};"
CMD8="E=\$(date '+%s'); echo \"denovo_map with M={{1}} n={{2}} m={{3}}: complete in\" \$(echo \"scale = 1; (\$E - \$S) / 60\" | bc) \"mins\";"

# combine commands
COMMANDS="$CMD1 $CMD2 $CMD3 $CMD4 $CMD5 $CMD6 $CMD7 $CMD8 $CMD9"

# run parallel jobs
parallel -j $PARALLEL_JOBS --no-notice "$COMMANDS" ::: ${{M_values[*]}} ::: ${{n_values[*]}} ::: ${{m_values[*]}}

# combine the results
head -n2 $(ls -1 $TMPDIR/stats/* | head -n1) | tail -n1 >> stats-phase2.tsv
for f in `ls -1 $TMPDIR/stats/*`; do
	tail -n+3 $f >> stats-phase2.tsv
done
cat $TMPDIR/stats/* >> stats-phase2a.tsv
rm -r $TMPDIR/stats

rad-pipeline_log Finished $0

