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
    
    parser.add_argument("-m", "--m-target", nargs=1, metavar='N', type=int, help="The target (i.e. centre) value to use for -m option.")
    parser.add_argument(      "--m-count", nargs=1, metavar='N', type=int, default=[2], help="The number of values to use either side of -m option. [Default: 2]")
    parser.add_argument("-n", "--n-target", nargs=1, metavar='N', type=int, help="The target (i.e. centre) value to use for -n option.")
    parser.add_argument(      "--n-count", nargs=1, metavar='N', type=int, default=[2], help="The number of values to use between d and D for -n option. [Default: 2]")
    parser.add_argument("-M", "--M-target", nargs=1, metavar='N', type=int, help="The target (i.e. centre) value to use for -M option.")
    parser.add_argument(      "--M-count", nargs=1, metavar='N', type=int, default=[2], help="The number of values to use between d and D for -n option. [Default: 2]")
    
    parser.add_argument("--denovo-opts", nargs=1, metavar='OPTS', default=["-S -t"], help="Other command line options to pass to denovo_map.pl. [Default: -S -t]")
    parser.add_argument("--keep-denovo-log", nargs=1, metavar='N', type=bool, default=[False], help="The batch id to use for denovo_map.pl [Default: False]")
    parser.add_argument("--batch-id", nargs=1, metavar='N', type=int, default=[2], help="The batch id to use for denovo_map.pl [Default: 2]")
    
    parser.add_argument("file", nargs="+", help="Files or directory to process.  If directory, -f filter is used to select files within.")
    parser.add_argument("-f", "--dir-filter", nargs=1, metavar='filter', default=["*.f*q"], help="A filter to match files when searching a directory.  [Default: *.f*q]")
    
    args = parser.parse_args(argv[1:])

    common.writecmd(argv)
    
    errors=False
    if args.m_target is None:
        sys.stderr.write("Error: option -m (--m-target) is required\n");
        errors=True
    if args.n_target is None:
        sys.stderr.write("Error: option -n (--n-target) is required\n");
        errors=True
    if args.M_target is None:
        sys.stderr.write("Error: option -M (--M-target) is required\n");
        errors=True
    if errors:
        return 1;
    
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
    
    subs['mvalues'] = " ".join(map(str, range(args.m_target[0]-args.m_count[0], args.m_target[0]+args.m_count[0]+1)))
    subs['nvalues'] = " ".join(map(str, range(args.n_target[0]-args.n_count[0], args.n_target[0]+args.n_count[0]+1)))
    subs['Mvalues'] = " ".join(map(str, range(args.M_target[0]-args.M_count[0], args.M_target[0]+args.M_count[0]+1)))
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

    
    jobscript = common.loadTemplate("denovo_opt2.slurm")
    if jobscript != "":
        print jobscript.format(**subs)
    else:
        sys.stderr.write("Error: failed to find template 'denovo_opt1.slurm'\n")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    sys.exit(main(sys.argv))
