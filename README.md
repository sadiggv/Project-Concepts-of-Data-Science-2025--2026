# Project-Concepts-of-Data-Science-2025--2026

# Bloom Filter Project

## Author

- Sadig Guliyev
- 2470331

## Project description

This repository contains an object-oriented implementation of a Bloom filter
in Python.

The implementation can be imported as a Python module in a Jupyter notebook or
used in a Python script on HPC infrastructure.

## Repository contents

- `bloom_filter.py`: Bloom filter implementation.
- `tests/test_bloom_filter.py`: correctness and hash-distribution tests.
- `benchmark.py`: benchmark of insertion, successful lookup, and unsuccessful
  lookup operations.
- `compression_analysis.py`: analysis of Bloom-filter compression ratio.
- `false_positive_experiment.py`: experiment measuring the Bloom filter false-positive rate.
- `run_benchmark.slurm`: Slurm job script for running the benchmark on the
  HPC cluster.
- `results/`: benchmark output files, CSV files, and plots produced after
  running the scripts.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally

Run the test suite:

```bash
python -m pytest
```

Run the benchmark and compression analysis:

```bash
python benchmark.py
python compression_analysis.py
```
