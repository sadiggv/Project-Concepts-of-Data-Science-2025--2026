# Project-Concepts-of-Data-Science-2025--2026

# Bloom Filter Project

## Author

- Sadig Guliyev
- [2410331]

## Project description

This repository contains an object-oriented implementation of a Bloom filter
in Python.

The implementation can be imported as a Python module in a Jupyter notebook or
used in a Python script on HPC infrastructure.

## Repository contents

- `bloom_filter.py`: Bloom filter implementation.
- `tests/test_bloom_filter.py`: correctness and hash-distribution tests.
- `benchmark.py`: benchmark of insertion, successful lookup and unsuccessful
  lookup operations.
- `compression_analysis.py`: analysis of Bloom-filter compression ratio.
- `run_benchmark.slurm`: SLURM job script for the HPC cluster.
- `results/`: benchmark output files, CSV files and plots after running the
  scripts.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
