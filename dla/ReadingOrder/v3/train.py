import os
import torch
from dataclasses import dataclass, field
from datasets import load_dataset, Dataset
from loguru import logger
from transformers import (
    TrainingArguments,
    HfArgumentParser,
    LayoutLMv3ForTokenClassification,
    set_seed,
)
from transformers.trainer import Trainer
from helpers import DataCollator, MAX_LEN

@dataclass
class Arguments(TrainingArguments):
    model_dir: str = field(
        default=None,
        metadata={"help": "Path to model, based on `microsoft/layoutlmv3-base`"},
    )
    dataset_dir: str = field(
        default=None,
        metadata={"help": "Path to dataset"},
    )

def load_train_and_dev_dataset(path: str) -> (Dataset, Dataset):
    datasets = load_dataset(
        "json",
        data_files={
            "train": os.path.join(path, "train.jsonl.gz"),
            "dev": os.path.join(path, "dev.jsonl.gz"),
        },
    )
    return datasets["train"], datasets["dev"]

def filter_long_samples(dataset):
    filtered_samples = []
    for i, sample in enumerate(dataset):
        if len(sample['source_boxes']) > MAX_LEN:
            logger.warning(f"Sample {i} exceeds MAX_LEN: {len(sample['source_boxes'])}")
        elif len(sample['source_texts']) > MAX_LEN:
            logger.warning(f"Sample {i} exceeds MAX_LEN: {len(sample['source_texts'])}")
        elif len(sample['target_boxes']) > MAX_LEN:
            logger.warning(f"Sample {i} exceeds MAX_LEN: {len(sample['target_boxes'])}")
        elif len(sample['target_texts']) > MAX_LEN:
            logger.warning(f"Sample {i} exceeds MAX_LEN: {len(sample['target_texts'])}")
        else:
            filtered_samples.append(sample)
    if filtered_samples:
        return Dataset.from_dict({key: [sample[key] for sample in filtered_samples] for key in filtered_samples[0].keys()})
    else:
        return Dataset.from_dict({key: [] for key in dataset[0].keys()})

def main():
    os.environ['MASTER_PORT'] = '29502'  # 변경된 포트 번호 설정
    os.environ['CUDA_LAUNCH_BLOCKING'] = '1'  # CUDA 런타임 오류 잡기

    parser = HfArgumentParser((Arguments,))
    args: Arguments = parser.parse_args_into_dataclasses()[0]
    set_seed(args.seed)

    train_dataset, dev_dataset = load_train_and_dev_dataset(args.dataset_dir)
    logger.info(
        "Train dataset size: {}, Dev dataset size: {}".format(
            len(train_dataset), len(dev_dataset)
        )
    )

    train_dataset = filter_long_samples(train_dataset)
    dev_dataset = filter_long_samples(dev_dataset)

    logger.info("Filtered train dataset size: {}".format(len(train_dataset)))
    logger.info("Filtered dev dataset size: {}".format(len(dev_dataset)))

    model = LayoutLMv3ForTokenClassification.from_pretrained(
        args.model_dir, num_labels=MAX_LEN, visual_embed=False
    )

    config = model.config
    logger.info(config.vocab_size)

    data_collator = DataCollator()

    class CustomTrainer(Trainer):
        def training_step(self, model, inputs):
            # 텐서의 모든 값을 프린트하도록 설정
            torch.set_printoptions(profile="full")

            # 입력 데이터의 형태와 크기 확인
            #logger.info("Inputs to the model:")
            for k, v in inputs.items():
                if isinstance(v, torch.Tensor):
                    #logger.info(f"{k}: shape {v.shape}, dtype {v.dtype}")
                    if k == 'input_ids':  # 임베딩 레이어에 들어가는 입력 데이터 확인
                        max_index = v.max().item()
                        min_index = v.min().item()
                        #logger.info(f"input_ids: {v}")
                        #logger.info(f"input_ids: max index {max_index}, min index {min_index}")
                        if max_index >= config.vocab_size or min_index < 0:
                            logger.warning(f"input_ids contain out of range values: {v}")
                    elif k == 'bbox':
                        max_bbox = v.max().item()
                        min_bbox = v.min().item()
                        #logger.info(f"bbox: {v}")
                        #logger.info(f"bbox: max value {max_bbox}, min value {min_bbox}")
                        if max_bbox > 1000 or min_bbox < 0:  # bbox 값의 범위를 적절히 설정
                            logger.warning(f"bbox contain out of range values: {v}")
                    elif k == 'attention_mask':
                        max_attention = v.max().item()
                        min_attention = v.min().item()
                        #logger.info(f"attention_mask: {v}")
                        #logger.info(f"attention_mask: max value {max_attention}, min value {min_attention}")
                        if max_attention > 1 or min_attention < 0:
                            logger.warning(f"attention_mask contain out of range values: {v}")
                    elif k == 'labels':
                        max_label = v[v != -100].max().item() if (v != -100).any() else -100
                        min_label = v[v != -100].min().item() if (v != -100).any() else -100
                        #logger.info(f"labels: {v}")
                        #logger.info(f"labels: max value {max_label}, min value {min_label}")
                        if max_label >= config.vocab_size or (min_label < 0 and min_label != -100):
                            logger.warning(f"labels contain out of range values: {v}")
                # else:
                #     logger.info(f"{k}: {v}")
            
            # 텐서 프린트 옵션을 기본값으로 되돌리기
            torch.set_printoptions(profile="default")

            return super().training_step(model, inputs)

    trainer = CustomTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        data_collator=data_collator,
    )

    try:
        trainer.train()
    except RuntimeError as e:
        logger.warning("An error occurred during training! ")
        for step, batch in enumerate(trainer.get_train_dataloader()):
            logger.warning(f"Step {step}:")
            for k, v in batch.items():
                if isinstance(v, torch.Tensor):
                    logger.warning(f"{k}: {v.shape}")
                else:
                    logger.warning(f"{k}: {v}")
            if step > 5:
                break
        raise e

if __name__ == "__main__":
    main()
