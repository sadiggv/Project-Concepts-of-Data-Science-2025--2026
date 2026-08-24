#!/bin/bash
#SBATCH --job-name=bloom_filter_benchmark
#SBATCH --output=results/slurm_%j.out
#SBATCH --error=results/slurm_%j.err
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

module load Python/3.11.5-GCCcore-13.2.0

python -m venv bloom_environment
source bloom_environment/bin/activate

pip install -r requirements.txt

mkdir -p results

python benchmark.py \
  --data-type words \
  --sizes 1000 10000 100000 1000000 \
  --output-directory results

python benchmark.py \
  --data-type dna \
  --sizes 1000 10000 100000 1000000 \
  --output-directory results/dna

python compression_analysis.py --output-directory results
