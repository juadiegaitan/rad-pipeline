#!/usr/bin/env python
# encoding: utf-8
'''
Generates a Slurm script for optimising stacks denovo_map.pl

@author:     Andrew Robinson
'''
import sys, argparse, os, subprocess

import common

def main(argv):
    ''''''
    parser = argparse.ArgumentParser(description='Generates a Slurm script for optimising stacks denovo_map.pl')
    
    parser.add_argument("-j", "--cores", nargs=1, metavar='N', type=int, default=[0], help="Total number of cores to use, 0=exclusive. [Default: 0]")
    parser.add_argument("--cores-task", nargs=1, metavar='T', type=int, default=[2], help="Number of cores each task (trial) uses. [Default: 2]")
    parser.add_argument("-p", "--partition", nargs=1, metavar="partition", default=["compute"], choices=['bigmem', '8hour', 'compute'], help="The partition (or queue) to submit job to")
    
    parser.add_argument("-m", "--m-range", nargs=1, metavar='d-D', default=["3-10"], help="The range of values to use for -m option. [Default: 3-10]")
    parser.add_argument(      "--m-count", nargs=1, metavar='N', type=int, default=[3], help="The number of values to use between d and D for -m option. [Default: 3]")
    parser.add_argument("-n", "--n-range", nargs=1, metavar='d-D', default=["5-20"], help="The range of values to use for -n option. [Default: 5-20]")
    parser.add_argument(      "--n-count", nargs=1, metavar='N', type=int, default=[4], help="The number of values to use between d and D for -n option. [Default: 4]")
    parser.add_argument("-M", "--M-range", nargs=1, metavar='d-D', default=["5-20"], help="The range of values to use for -n option. [Default: 5-20]")
    parser.add_argument(      "--M-count", nargs=1, metavar='N', type=int, default=[4], help="The number of values to use between d and D for -n option. [Default: 4]")
    
    parser.add_argument("--denovo-opts", nargs=1, metavar='OPTS', default=["-S -t"], help="Other command line options to pass to denovo_map.pl. [Default: -S -t]")
    parser.add_argument("--keep-denovo-log", nargs=1, metavar='N', type=bool, default=[False], help="Keep the denovo_log files for each trial [Default: 0 (False)]")
    parser.add_argument("--batch-id", nargs=1, metavar='N', type=int, default=[1], help="The batch id to use for denovo_map.pl [Default: 1]")
    
    parser.add_argument("file", nargs="+", help="Files or directory to process.  If directory, -f filter is used to select files within.")
    parser.add_argument("-f", "--dir-filter", nargs=1, metavar='filter', default=["*.f*q"], help="A filter to match files when searching a directory.  [Default: *.f*q]")
    
    args = parser.parse_args(argv[1:])

    common.writecmd(argv)
    
    
    ## make the variable parts of script
    subs = {}
    if args.cores[0] == 0:
        subs['slurmheader'] = common.makeExclusiveHeader(partition=args.partition[0], mem="64000")
        args.cores[0] = 16
    else:
        subs['slurmheader'] = common.makeHeader(partition=args.partition[0], ntasks=args.cores[0])
    files = []
    for f in args.file:
        if '*' in f or '?' in f or os.path.exists(f):
            if os.path.isdir(f):
                files.append("%s/%s" % (f, args.dir_filter[0]))
            else:
                files.append(f)
        else:
            sys.stderr.write("Warning: file '%s' does not exist and will be ignored\n"%f)
            
    subs['files'] = " ".join(files)
    subs['stacksversion'] = subprocess.check_output(["rad-pipeline_module_version", "stacks-gcc"]).rstrip()
    vars["parallelversion"] = subprocess.check_output(["rad-pipeline_module_version", "parallel"]).rstrip()
    vars["radpipelineversion"] = subprocess.check_output(["rad-pipeline_module_version", "rad-pipeline"]).rstrip()
    
    subs['mrange'] = " ".join(args.m_range[0].split('-'))
    subs['mcount'] = str(args.m_count[0])
    subs['nrange'] = " ".join(args.n_range[0].split('-'))
    subs['ncount'] = str(args.n_count[0])
    subs['Mrange'] = " ".join(args.M_range[0].split('-'))
    subs['Mcount'] = str(args.M_count[0])
    subs['CMD'] = " ".join(argv)
    
    if args.keep_denovo_log[0]:
        subs['nocpdenovo'] = ""
    else:
        subs['nocpdenovo'] = "#"
    
    subs['corestask'] = args.cores_task[0]
    subs['paralleljobs'] = str(int(args.cores[0] / args.cores_task[0]))
    subs['denovoopts'] = args.denovo_opts[0]
    subs['batchid'] = args.batch_id[0]

    ## validate inputs ##
    filecount = 0
    if len(files) > 0:
        cmd = ["bash", "-c", 'ls -1 %s'%(" ".join(files))]
        #cmd.extend(files)
        filelist = subprocess.check_output(cmd).rstrip()
        #print "'%s'"%filelist
        filecount = len(filelist.split("\n"))

    if filecount < 2 or filecount > 6:
        sys.stderr.write("Warning: suboptimal number of samples (%s).  You should use 2 to 6 representitive samples.\n"%filecount)

    
    jobscript = common.loadTemplate("denovo_opt1.slurm")
    if jobscript != "":
        print jobscript.format(**subs)
    else:
        sys.stderr.write("Error: failed to find template 'denovo_opt1.slurm'\n")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    sys.exit(main(sys.argv))
