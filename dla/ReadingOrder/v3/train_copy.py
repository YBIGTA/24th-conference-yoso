import os

import torch
from dataclasses import dataclass, field

from datasets import load_dataset, Dataset, DatasetDict
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
        if len(sample['source_texts']) > MAX_LEN:
            logger.warning(f"Sample {i} exceeds MAX_LEN: {len(sample['source_texts'])}")
        else:
            filtered_samples.append(sample)
    if filtered_samples:
        return Dataset.from_dict({key: [sample[key] for sample in filtered_samples] for key in filtered_samples[0].keys()})
    else:
        return Dataset.from_dict({key: [] for key in dataset[0].keys()})

def main():
    parser = HfArgumentParser((Arguments,))
    args: Arguments = parser.parse_args_into_dataclasses()[0]
    set_seed(args.seed)

    train_dataset, dev_dataset = load_train_and_dev_dataset(args.dataset_dir)
    logger.info(
        "Train dataset size: {}, Dev dataset size: {}".format(
            len(train_dataset), len(dev_dataset)
        )
    )

    # MAX_LEN과 각 샘플의 source_texts 길이를 확인하고 초과하는 샘플 제거
    train_dataset = filter_long_samples(train_dataset)
    dev_dataset = filter_long_samples(dev_dataset)

    logger.info("Filtered train dataset size: {}".format(len(train_dataset)))
    logger.info("Filtered dev dataset size: {}".format(len(dev_dataset)))

    # 각 샘플의 source_boxes와 target_boxes 길이를 출력하여 확인
    for i, sample in enumerate(train_dataset):
        if len(sample['source_boxes']) != len(sample['source_texts']):
            logger.warning(f"Sample {i} has mismatched lengths for source_boxes ({len(sample['source_boxes'])}) and source_texts ({len(sample['source_texts'])})")
        if len(sample['target_boxes']) != len(sample['target_texts']):
            logger.warning(f"Sample {i} has mismatched lengths for target_boxes ({len(sample['target_boxes'])}) and target_texts ({len(sample['target_texts'])})")
        if len(sample['target_boxes']) != len(sample['source_boxes']):
            logger.warning(f"Sample {i} has mismatched lengths for source_boxes ({len(sample['source_boxes'])}) and target_boxes ({len(sample['target_boxes'])})")

    model = LayoutLMv3ForTokenClassification.from_pretrained(
        args.model_dir, num_labels=MAX_LEN, visual_embed=False
    )
    data_collator = DataCollator()
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=dev_dataset,
        data_collator=data_collator,
    )

    try:
        print(len(train_dataset))
        breakpoint()
        trainer.train()
    except RuntimeError as e:
        # 디버깅 정보를 출력합니다.
        logger.warning("An error occurred during training! ")
        for step, batch in enumerate(trainer.get_train_dataloader()):
            logger.warning(f"Step {step}:")
            for k, v in batch.items():
                if isinstance(v, torch.Tensor):
                    logger.warning(f"{k}: {v.shape}")
                else:
                    logger.warning(f"{k}: {v}")
            if step > 5:  # 예시로 첫 5개 배치만 출력
                break
        raise e

if __name__ == "__main__":
    main()
