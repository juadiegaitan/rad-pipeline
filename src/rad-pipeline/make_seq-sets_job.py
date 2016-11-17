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

Generates a Slurm script for running seq-sets on a collection of raw and kraken files

@author:     Andrew Robinson
'''
import sys, argparse, os, subprocess

import common

def main(argv):
    ''''''
    parser = argparse.ArgumentParser(description='Generates a slurm script for running seq-sets of a selection of raw and kraken files')
    
    #parser.add_argument("-j", "--cores", nargs=1, metavar='N', type=int, default=[0], help="The maximum number of cores to use, 0=exclusive. [Default: 0]")
    parser.add_argument("-p", "--partition", nargs=1, metavar="partition", default=["8hour"], choices=['bigmem', '8hour', 'compute'], help="The partition (or queue) to submit job to")
    parser.add_argument("rawfile", nargs="+", help="Files or directory of raw fastq/a sequences to filter.  If directory, -f filter is used to select files within.")
    parser.add_argument("-f", "--dir-filter", nargs=1, metavar='filter', default=["*.f*q"], help="A filter to match files when searching a directory.  [Default: \"*.f*q]\"")
    parser.add_argument("-k", "--kraken-file", nargs="+", help="Files or directory of kraken_classified fastq/a sequences.  If directory, -K filter is used to select files within.")
    parser.add_argument("-K", "--kraken-dir-filter", nargs=1, metavar='filter', default=["*_classified.f*q"], help="A filter to match files when searching a kraken result directory.  [Default: \"*_classified.f*q\"]")
    
    args = parser.parse_args(argv[1:])
    
    common.writecmd(argv)
    
    #print args

    # expand files
    rawfiles=common.expandFiles(args.rawfile, args.dir_filter[0])
    krakenfiles=common.expandFiles(args.kraken_file, args.kraken_dir_filter[0])

    error=False
    if len(rawfiles) == 0:
        sys.stderr.write("No RAW files found: '%s'\n" % (" ".join(args.rawfile)))
        error=True
    if len(krakenfiles) == 0:
        sys.stderr.write("No KRAKEN files found: '%s'\n" % (" ".join(args.kraken_file)))
        error=True
    if error:
        return 1
    
    ## make the variable parts of script
    vars={}
    vars["rawfiles"] = " ".join(rawfiles)
    vars["krakenfiles"] = " ".join(krakenfiles)
    #if args.cores[0] == 0:
    #    vars["slurmheader"] = common.makeExclusiveHeader(partition=args.partition[0])
    #else:
    #    vars["slurmheader"] = common.makeHeader(partition=args.partition[0], ntasks=args.cores[0])
    vars["slurmheader"] = common.makeHeader(partition=args.partition[0], cores=1)
    vars["biostreamtoolsversion"] = subprocess.check_output(["rad-pipeline_module_version", "biostreamtools"]).rstrip()
    vars["parallelversion"] = subprocess.check_output(["rad-pipeline_module_version", "parallel"]).rstrip()
    vars["radpipelineversion"] = subprocess.check_output(["rad-pipeline_module_version", "rad-pipeline"]).rstrip()
    vars["CMD"] = " ".join(argv)
    
    jobscript = common.loadTemplate("seqsets.slurm")
    
    print jobscript.format(**vars)
    
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    sys.exit(main(sys.argv))

