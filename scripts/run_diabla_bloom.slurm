#!/bin/bash
#SBATCH -C a100
#SBATCH --partition=gpu_p5
#SBATCH -A ncm@a100
#SBATCH --gres=gpu:8
#SBATCH --cpus-per-task=64           # number of cores per task (with gpu_p2: 1/8 of the 8-GPUs node)  
#SBATCH --job-name=diabla   # nom du job
#SBATCH --ntasks=1             # Nombre total de processus MPI
#SBATCH --ntasks-per-node=1    # Nombre de processus MPI par noeud
# Dans le vocabulaire Slurm "multithread" fait référence à l'hyperthreading.
#SBATCH --hint=nomultithread   # 1 processus MPI par coeur physique (pas d'hyperthreading)
#SBATCH --time=20:00:00        # Temps d’exécution maximum demande (HH:MM:SS)
#SBATCH --output=diabla_%j.out  # Nom du fichier de sortie contenant l'ID et l'indice
#SBATCH --error=diabla_%j.out   # Nom du fichier d'erreur (ici commun avec la sortie)

# go into the submission directory 
cd ${SLURM_SUBMIT_DIR}

maindir=/gpfswork/rech/ncm/ulv12mq/lm-evaluation-harness
outputdir=$maindir/outputs
[ -d $outputdir ] || mkdir $outputdir

modelname=bloom
modelpath=/gpfsdswork/dataset/HuggingFace_Models/bigscience/bloom # best to work from a local copy

# choose a task and comment out the others
task=diabla # default task
#task=diabla_1_shot_context_opposite # in a 1-shot setting, use previous context from the opposite direction from the current example
#task=diabla_1_shot_context_same # in a 1-shot setting, use previous context from the same direction as current example
#task=diabla_1_shot_context_orig # in a 1-shot setting, use previous context from the original direction of the few-shot example

template=xglm

# choose a few-shot number
fewshotnum=1
#fewshotnum=0

seed=1234
timestamp=$(date +"%Y-%m-%dT%H_%M_%S")
output="model=$modelname.task=$task.templates=$template.fewshot=$fewshotnum.seed=$seed.timestamp=$timestamp"
batchsize=8

# need those modules for it to work on JZ
#module load cpuarch/amd
#module load pytorch-gpu/py3/1.11.0
#module load cuda/11.2

export CUDA_LAUNCH_BLOCKING=1
echo "Writing to: $output"
TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
TOKENIZERS_PARALLELISM=false \
python $maindir/main.py --model_api_name 'hf-causal' --model_args "use_accelerate=True,pretrained=$modelpath,tokenizer=$modelpath,dtype=bfloat16" \
       --task_name $task --template_names $template --num_fewshot $fewshotnum --seed $seed --output_path $output --batch_size $batchsize --no_tracking --device cuda  --use_cache --bootstrap_iters 1
