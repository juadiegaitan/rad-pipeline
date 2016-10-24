#!/usr/bin/env python
# encoding: utf-8
'''
Generates a Slurm script for running kraken on a collection of files

@author:     Andrew Robinson
'''
import sys, argparse, os, subprocess

import common

def main(argv):
    ''''''
    parser = argparse.ArgumentParser(description='Generates a slurm script for running kraken of a selection of files')
    
    parser.add_argument("-j", "--cores", nargs=1, metavar='N', type=int, default=[0], help="The number of cores to use, 0=exclusive. [Default: 0]")
    parser.add_argument("-p", "--partition", nargs=1, metavar="partition", default=["bigmem"], choices=['bigmem', '8hour', 'compute'], help="The partition (or queue) to submit job to")
    parser.add_argument("file", nargs="+", help="Files or directory to process.  If directory, -f filter is used to select files within.")
    parser.add_argument("-f", "--dir-filter", nargs=1, metavar='filter', default=["*.fastq"], help="A filter to match files when searching a directory.  [Default: \\*.fastq]")
    
    args = parser.parse_args(argv[1:])
    
    common.writecmd(argv)
    
    #print args
    
    ## make the variable parts of script
    vars={}
    if args.cores[0] == 0:
        vars["slurmheader"] = common.makeExclusiveHeader(partition=args.partition[0])
    else:
        vars["slurmheader"] = common.makeHeader(partition=args.partition[0], ntasks=args.cores[0])
    files = []
    for f in args.file:
        if '*' in f or '?' in f or os.path.exists(f):
            if os.path.isdir(f):
                files.append("%s/%s" % (f, args.dir_filter[0]))
            else:
                files.append(f)
        else:
            sys.stderr.write("Warning: file '%s' does not exist and will be ignored\n")
            
    vars["files"] = " ".join(files)
    vars["krakenversion"] = subprocess.check_output(["rad-pipeline_module_version", "kraken"]).rstrip()
    vars["radpipelineversion"] = subprocess.check_output(["rad-pipeline_module_version", "rad-pipeline"]).rstrip()
    vars["CMD"] = " ".join(argv)
    
    jobscript = common.loadTemplate("kraken.slurm")
    
    print jobscript.format(**vars)
    
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    sys.exit(main(sys.argv))

