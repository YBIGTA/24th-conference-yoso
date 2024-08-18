#!/usr/bin/env bash

set -x
set -e

DIR="$( cd "$( dirname "$0" )" && cd .. && pwd )"
OUTPUT_DIR="${DIR}/checkpoint/v3/$(date '+%Y-%m-%d-%H%M%S')"
DATA_DIR="${DIR}/data_texted/"

mkdir -p "${OUTPUT_DIR}"

export CUDA_LAUNCH_BLOCKING=1  # 추가된 부분

deepspeed train.py \
  --model_dir 'hantian/layoutreader' \
  --dataset_dir "${DATA_DIR}" \
  --dataloader_num_workers 4 \
  --deepspeed ds_config.json \
  --per_device_train_batch_size 32 \
  --per_device_eval_batch_size 64 \
  --do_train \
  --do_eval \
  --logging_steps 100 \
  --bf16 \
  --seed 42 \
  --num_train_epochs 10 \
  --learning_rate 5e-5 \
  --warmup_steps 100 \
  --save_strategy epoch \
  --evaluation_strategy epoch \
  --remove_unused_columns False \
  --output_dir "${OUTPUT_DIR}" \
  --overwrite_output_dir True \
  "$@"
