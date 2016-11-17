#!/usr/bin/env python
# encoding: utf-8

'''
#########################################################################################
# BSD 3-Clause License                                                                  #
#                                                                                       #
# Copyright (c) 2016, Andrew Robinson and La Trobe University                           #
# All rights reserved.                                                                  #
#                                                                                       #
# Redistribution and use in source and binary forms, with or without                    #
# modification, are permitted provided that the following conditions are met:           #
#                                                                                       #
# * Redistributions of source code must retain the above copyright notice, this         #
#   list of conditions and the following disclaimer.                                    #
#                                                                                       #
# * Redistributions in binary form must reproduce the above copyright notice,           #
#   this list of conditions and the following disclaimer in the documentation           #
#   and/or other materials provided with the distribution.                              #
#                                                                                       #
# * Neither the name of the copyright holder nor the names of its                       #
#   contributors may be used to endorse or promote products derived from                #
#   this software without specific prior written permission.                            #
#                                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"           #
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE             #
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE        #
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE          #
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL            #
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR            #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER            #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,         #
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE         #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.                  #
#########################################################################################

Generates a Slurm script for running demultiplex_radtags on a collection of files

@author:     Andrew Robinson
'''
import sys, argparse, os, subprocess

import common, time

def main(argv):
    ''''''
    parser = argparse.ArgumentParser(description='Generates a slurm script for running demultiplex_radtags on a selection of files')
    
    #parser.add_argument("-j", "--cores", nargs=1, metavar='N', type=int, default=[1], help="The number of cores to use, 0=exclusive. [Default: 1]")
    parser.add_argument("-p", "--partition", nargs=1, metavar="partition", default=["8hour"], choices=['bigmem', '8hour', 'compute'], help="The partition (or queue) to submit job to  [Default: 8hour]")
    parser.add_argument("file", nargs="+", help="(Read 1) Files or directory to process.  If directory, -f filter is used to select files within.")
    parser.add_argument("-f", "--dir-filter", nargs=1, metavar='filter', default=["*_R1_*.f*q*"], help="A filter to match files when searching a directory.  [Default: \"*_R1_*.f*q*\"]")
    parser.add_argument("-t", "--time", nargs=1, metavar='time', default=["01:00:00"], help="Job max runtime.  [Default: 01:00:00]")
    parser.add_argument("-e", "--enzyme", nargs='+', metavar='enzyme', default=["ecoRI"], help="1 or 2 enzymes used for cut sites.  [Default: ecoRI]")
    parser.add_argument("-r", "--no-remainder", action='store_true', help="Don't include the remainder (singleton) reads in output  [Default: notset (i.e. include them)]")
    
    args = parser.parse_args(argv[1:])

    common.writecmd(argv)
    
    #print args
    
    ## make the variable parts of script
    vars={}
    #if args.cores[0] == 0:
    #    vars["cores"] = "16"
    #else:
    #    vars["cores"] = args.cores[0]
    #if vars["cores"] > 8 and args.partition[0] == "8hour":
    #    args.partition[0] = "compute"
    #if args.cores[0] == 0:
    #    vars["slurmheader"] = common.makeExclusiveHeader(partition=args.partition[0], time=args.time[0])
    #else:
    vars["slurmheader"] = common.makeHeader(partition=args.partition[0], ntasks=1, time=args.time[0])
    vars["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if len(args.enzyme) > 1:
        vars["enzymes"] = "--renz_1 %s --renz_2 %s" % (args.enzyme[0], args.enzyme[1])
    else:
        vars["enzymes"] = "-e %s" % (args.enzyme[0],)
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
    vars["stacksversion"] = subprocess.check_output(["rad-pipeline_module_version", "stacks-gcc"]).rstrip()
    vars["radpipelineversion"] = subprocess.check_output(["rad-pipeline_module_version", "rad-pipeline"]).rstrip()
    vars["CMD"] = " ".join(argv)
    if args.no_remainder:
        vars["norem"] = "#"
    else:
        vars["norem"] = ""

    
    jobscript = common.loadTemplate("demux.slurm")
    
    print jobscript.format(**vars)
    
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    sys.exit(main(sys.argv))


