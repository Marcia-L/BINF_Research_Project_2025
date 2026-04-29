#!/bin/bash
#SBATCH --job-name="hongru_python_script"
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=12:00:00
#SBATCH --account=punim2700
#SBATCH --partition=sapphire
#SBATCH --mem=16GB


# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/home/hongrul2/miniforge3/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/home/hongrul2/miniforge3/etc/profile.d/conda.sh" ]; then
        . "/home/hongrul2/miniforge3/etc/profile.d/conda.sh"
    else
        export PATH="/home/hongrul2/miniforge3/bin:$PATH"
    fi
fi
unset __conda_setup

# <<< conda initialize <<<
conda activate baseline


CMD="$@"
echo $CMD
eval $CMD

my-job-stats -a -n -s
