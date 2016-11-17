{slurmheader}

###
# Author:      Andrew Robinson
# Date:        2014-12-22
# Description: Runs fastqc on each file provided in FILES Setting (and deletes the zipfile)
###

# Command used to generate this file:
# {CMD}

## SETTINGS ##

FILES="{rawfiles}"

CORES={cores}

## End SETTINGS ##

# load modules
module load fastqc/{fastqcversion} parallel/{parallelversion}  rad-pipeline/{radpipelineversion}

rad-pipeline_log Starting $0

## do work ##
FILESEXP=`ls -1 $FILES`
#FILECOUNT=`ls -1 $FILES | wc -l`

CMD="echo \"fastqc {{1}}\"; fastqc -o . {{1}}; export f=\$(basename {{1}}); rm \"\${{f%.*}}_fastqc.zip\";"

parallel -j $CORES  --no-notice "$CMD" ::: $FILESEXP

rad-pipeline_log Finished $0

