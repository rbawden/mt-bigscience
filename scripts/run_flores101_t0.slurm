#!/bin/bash
#SBATCH -C v100-32g
#SBATCH -A ncm@v100
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=16           # number of cores per task (with gpu_p2: 1/8 of the 8-GPUs node)  
#SBATCH --job-name=flores   # nom du job
#SBATCH --ntasks=1             # Nombre total de processus MPI
#SBATCH --ntasks-per-node=1    # Nombre de processus MPI par noeud
# Dans le vocabulaire Slurm "multithread" fait référence à l'hyperthreading.
#SBATCH --hint=nomultithread   # 1 processus MPI par coeur physique (pas d'hyperthreading)
#SBATCH --time=12:00:00        # Temps d’exécution maximum demande (HH:MM:SS)
#SBATCH --output=flores_T0_%j.out  # Nom du fichier de sortie contenant l'ID et l'indice
#SBATCH --error=flores_T0_%j.out   # Nom du fichier d'erreur (ici commun avec la sortie)

# go into the submission directory 
cd ${SLURM_SUBMIT_DIR}

maindir=/gpfswork/rech/ncm/ulv12mq/lm-evaluation-harness
outputdir=$maindir/runs/outputs
[ -d $outputdir ] || mkdir $outputdir

modelname=t0
modelpath=bigscience/T0
tokeniserpath=$modelpath

task=flores_101_mt

# choose a template and commet out the others
template=flores-xglm-French-English
#template=flores-xglm-English-French
#template=flores-xglm-English-Hindi
#template=flores-xglm-Hindi-English

# choose the fewshot number and comment the other
fewshotnum=1
#fewshotnum=0

seed=1234
timestamp=$(date +"%Y-%m-%dT%H_%M_%S")
output="model=$modelname.task=$task.templates=$template.fewshot=$fewshotnum.seed=$seed.timestamp=$timestamp"
batchsize=4

echo "Writing to: $output"
export CUDA_LAUNCH_BLOCKING=1
TRANSFORMERS_OFFLINE=1 HF_DATASETS_OFFLINE=1 \
TOKENIZERS_PARALLELISM=false \
python $maindir/main.py --model_api_name 'hf-seq2seq' --model_args "use_accelerate=True,pretrained=$modelpath,tokenizer=$tokeniserpath,dtype=float32" \
    --task_name $task --template_names "$template" --num_fewshot $fewshotnum --seed $seed --output_path "$output" --batch_size $batchsize --no_tracking --use_cache --device cuda
