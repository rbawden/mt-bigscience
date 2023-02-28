#!/bin/bash
#SBATCH -C a100
#SBATCH --partition=gpu_p5
#SBATCH -A lmy@a100
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=64           # number of cores per task (with gpu_p2: 1/8 of the 8-GPUs node)  
#SBATCH --job-name=flores   # nom du job
#SBATCH --ntasks=1             # Nombre total de processus MPI
#SBATCH --ntasks-per-node=1    # Nombre de processus MPI par noeud
# Dans le vocabulaire Slurm "multithread" fait référence à l'hyperthreading.
#SBATCH --hint=nomultithread   # 1 processus MPI par coeur physique (pas d'hyperthreading)
#SBATCH --time=8:00:00        # Temps d’exécution maximum demande (HH:MM:SS)
#SBATCH --output=flores_bloom_%j.out  # Nom du fichier de sortie contenant l'ID et l'indice
#SBATCH --error=flores_bloom_%j.out   # Nom du fichier d'erreur (ici commun avec la sortie)

# go into the submission directory 
cd ${SLURM_SUBMIT_DIR}

maindir=/gpfswork/rech/ncm/ulv12mq/lm-evaluation-harness
outputdir=$maindir/runs/outputs
[ -d $outputdir ] || mkdir $outputdir

modelname=bloom
modelpath=/gpfsdswork/dataset/HuggingFace_Models/bigscience/bloom

# choose one of these tasks and comment out the others
task=flores_101_mt # default task
#task=flores_101_mt_fewshot_en2bn # use en2bn few-shot examples
#task=flores_101_mt_fewshot_fr2ar # use fr2ar few-shot examples
#task=flores_101_mt_fewshot_fr2en # use fr2en few-shot examples
#task=flores_101_mt_fewshot_hi2en # use hi2en few-shot examples
#task=flores_101_mt_fewshot_wmt_hi2en # use hi2en few-shot examples but from WMT

# choose a template here (full list available in PromptSource)
template=flores-xglm-Bengali-English
#template=flores-xglm-Hindi-English
#template=flores-xglm-English-Hindi
#template=flores-xglm-English-French
#template=flores-xglm-French-English
#template="flores-xglm-Yoruba-Swahili"

# choose a fewshot number
#fewshotnum=1
fewshotnum=0

seed=1234
timestamp=$(date +"%Y-%m-%dT%H_%M_%S")
output="model=$modelname.task=$task.templates=$template.fewshot=$fewshotnum.seed=$seed.timestamp=$timestamp"
batchsize=4

# need these models to make it work on Jean-Zay
#module load cpuarch/amd
#module load pytorch-gpu/py3/1.11.0
#module load cuda/11.2

export CUDA_LAUNCH_BLOCKING=1
echo "Writing to: $output"
TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
TOKENIZERS_PARALLELISM=false \
python $maindir/main.py --model_api_name 'hf-causal' --model_args "use_accelerate=True,pretrained=$modelpath,tokenizer=$modelpath,dtype=bfloat16" \
    --task_name $task --template_names "$template" --num_fewshot $fewshotnum --seed $seed --output_path "$output" --batch_size $batchsize --no_tracking --use_cache --device cuda 
