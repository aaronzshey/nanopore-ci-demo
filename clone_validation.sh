#!/bin/sh
#SBATCH --time=2:00:00
#SBATCH --partition=savio3_htc
#SBATCH --account=fc_fpsdnaseq
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4

# clone_validation.sh 
# this program takes in Run ID ${1) and barcode number ${2}

# by Aaron Shey, March 21 2025

ml openjdk

export WDIR=/global/home/groups/fc_fpsdnaseq

export NXF_WORK=/global/scratch/users/brianmcc/work{2}
export NXF_SINGULARITY_CACHEDIR=/global/scratch/users/brianmcc/container/singularity
echo "NXF_SINGULARITY_CACHEDIR is "${NXF_SINGULARITY_CACHEDIR}""
echo "NXF_WORK directory is "${NXF_WORK}""

cd /global/scratch/users/aaronshey

./nextflow run epi2me-labs/wf-clone-validation --fastq ${WDIR}/${1}/plate1_tmp/${2} --db-directory wf-clone-validation-db --sample_sheet ${WDIR}/${1}/${1}_size_sheet.csv --out_dir ${WDIR}/${1}/clone-validation/plate1/${2} -profile singularity --threads 2

# clean up

./nextflow clean -f
rm -rf /global/scratch/users/brianmcc/work{2}
