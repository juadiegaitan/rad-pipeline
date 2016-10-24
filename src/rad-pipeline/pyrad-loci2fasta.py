#!/bin/env python

# converts the pyRAD loci file into fasta format

import sys

if len(sys.argv) != 2:
	print "Usage: pyrad-loci2fasta LOCIFILE [> OUTPUTFILE]"
	sys.exit(1)

FILENAME=sys.argv[1]

## read in your data file
infile = open(FILENAME, "r")

## parse the loci in your data file
data = infile.read()
locid = data.split("\n//")
loci = locid[:-1]

## write the first read from each locus to the output file in fasta format
for loc in loci:
	reads = loc.split("\n",2)
	name, seq = reads[1].split()
	print name+"\n"+seq

infile.close()

