#!/bin/env python
'''
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2014 Andrew Robinson <andrewjrobinson@gmail.com>        * 
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

Created on 12 Mar 2015

Computes a summary and consensus sequence for each feature

@author: arobinson
'''

import sys


def _usage(argv):
    progname = "pyrad-feature-summary"
    if len(argv) > 0:
        progname = argv[0]
    print ("")
    print ("usage: %s -h" % progname)
    print ("usage: %s locifile.loci featurefile.vcf" % progname)
    print ("")
    if '-h' in argv or '--help' in argv:
        print ("Computes a summary and consensus sequence for each feature")
        print ("")
    print (" locifile.loci    File containing the loci sequences for each sample found at the loci.")
    print (" featurefile.vcf  File containing features of interest.  This is generally") 
    print ("                  a filtered version of the vcf output from pyRAD.")
    print ("")


def _main(argv):
    '''Application main function'''
    
    if len(argv) != 3:
        _usage(argv)
        return 1
        
    locifilename = argv[1]
    vcffilename = argv[2]
    
    ## stage 1: construct consensus
    consensus = {}
    with open(locifilename) as f:
        _sequences = []
        _samples   = []
        for line in f:
            line = line.rstrip()
            if line.startswith("//"):
                _, _contigid = line.split("|", 1)
                cons = makeConsensus(_sequences)
                consensus[_contigid] = (cons, _samples)
                
                ## check concensus
#                 print "Contig: %s" % _contigid
#                 for s in _sequences:
#                     print "S: %s" % s
#                  
#                 print "C: %s" % cons
#                 print ""
                
                _sequences = []
                _samples   = []
            elif len(line) > 0:
                seqid, seq = line.split()
                _sequences.append(seq)
                _samples.append(seqid[1:])
    
#     for key, value in consensus.items():
#         print ("%s: %s" %(key, value))
    
    ## stage 2: merge features with consensus
    with open(vcffilename) as f:
        for line in f:
            if not line.startswith("##"):
                fields = line.split("\t", 8)[:8]
                 
                if line.startswith("#"):
                    print "SNP_ID\tCONTIG#\t%s\tCONSENSUS\tMEMBERS" % ("\t".join(fields[1:]))
                else:
                    if len(fields) > 3:
                        pos = int(fields[1])
                        cons, members = consensus[fields[0]]
    #                     consf = cons
                        consf = "%s<%s>%s" % (cons[:pos-1], cons[pos-1], cons[pos:])
                        print "%s\t%s\t%s\t%s" %(":".join(fields[0:2]), 
                                                 "\t".join(fields),
                                                 consf,
                                                 ",".join(members)
                                                )
                        
    
    
    return 0
# end _main()


def makeConsensus(sequences):
    '''Creates a consensus sequence from provided sequences'''
    
    if len(sequences) > 0:
        result = ""
        for i in xrange(len(sequences[0])):
            
            # count bases at this position
            counts = {}
            for seq in sequences:
                b = seq[i]
                if b in counts:
                    counts[b] += 1
                else:
                    counts[b] = 1
            
            # find most abundant
            largest = ('N', 0)
            while len(counts) > 0:
                c = counts.popitem()
                if c[1] > largest[1] and c[0] not in ('-', 'N'):
                    largest = c
            
            result += largest[0]
            
        # next i (sequence index)
        return result
    return ""
    
    
if __name__ == '__main__':
    if len(sys.argv) == 1 and sys.stdin.isatty() or '-h' in sys.argv or '--help' in sys.argv:
        _usage(sys.argv)
        sys.exit(0)
    else:
        sys.exit(_main(sys.argv))
        

