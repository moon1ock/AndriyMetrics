#!/bin/bash
#SBATCH -p bigmem
#SBATCH --mail-user=aal544
#SBATCH --mail-type=END,FAIL
#SBATCH --mem 512GB
#SBATCH --time=24:00:00

module purge

source ~/.bashrc
conda activate /scratch/aal544/conda-envs/venv/

python run.py