#!/bin/bash
#SBATCH --job-name=spweights
#SBATCH --output=spweights_job_%j.out
#SBATCH --error=spweights_job_%j.err
#SBATCH --partition=compute
#SBATCH --time=4:00:00
#SBATCH --mem=16G
#SBATCH --n-tasks=1
#SBATCH --cpus-per-task=4

module load apps/python3

eval "$(conda shell.bash hook)"
conda activate npl-2024b

cd /beegfs/sets/aw-ciroh/projects/LE_lstm_eval

python scripts/run_spweights.py "$GRID_NAME" "$MAPPING_NC_NAME"