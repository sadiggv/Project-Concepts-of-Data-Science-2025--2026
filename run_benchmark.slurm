#!/bin/bash -l
#SBATCH --job-name=bloom_filter
#SBATCH --output=slurm_%j.out
#SBATCH --error=slurm_%j.err
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

module load Miniforge3/25.3.0-3

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$VSC_DATA/bloom-filter-env"

echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "Slurm job ID: $SLURM_JOB_ID"
echo "Cluster: $SLURM_CLUSTER_NAME"
echo "Python version:"
python --version

mkdir -p results

python benchmark.py \
  --data-type words \
  --sizes 1000 10000 100000 1000000 \
  --output-directory results/words

python benchmark.py \
  --data-type dna \
  --sizes 1000 10000 100000 1000000 \
  --output-directory results/dna

python false_positive_experiment.py \
  --expected-items 100000 \
  --false-positive-rate 0.01 \
  --output-directory results

python compression_analysis.py \
  --output-directory results
