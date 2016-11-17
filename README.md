# RADseq Pipeline

A RADseq pipeline based on a read-cluster approach

## Installation

### Dependencies

* Stacks ([http://catchenlab.life.illinois.edu/stacks/](http://catchenlab.life.illinois.edu/stacks/))
* Python (tested with v2.7.6)
* Parallel (http://www.gnu.org/software/parallel/) [Version 20140722 was used when testing]
* SLURM HPC
* Environment Modules 

### rad-pipeline

1. Download the latest release
2. Extract archive
3. Add bin directory to your path

e.g.

```sh
wget https://github.com/molecularbiodiversity/rad-pipeline/archive/v0.1.0.tar.gz
tar xf v0.1.0.tar.gz
export PATH=$PATH:$PWD/rad-pipeline-0.1/bin
```

## Getting Started

[User Manual](docs/index.md)

## License

rad-pipeline is licensed under the BSD 3-clause open-source license.  Please 
refer to LICENSE file for details