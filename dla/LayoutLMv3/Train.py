## Python imports
import argparse
import warnings
import numpy as np
warnings.filterwarnings("ignore", category=UserWarning)
## Huggingface imports
from datasets import load_metric
from transformers import AutoProcessor
from transformers import TrainingArguments, Trainer
from transformers import LayoutLMv3ForTokenClassification
from transformers.data.data_collator import default_data_collator
## Custom imports
from Dataset import prepare_doclaynet


label_list = ['Caption',
              'Footnote',
              'Formula',
              'List-item',
              'Page-footer',
              'Page-header',
              'Picture',
              'Section-header',
              'Table',
              'Text',
              'Title']

id2label = {0: 'Caption',
            1: 'Footnote',
            2: 'Formula',
            3: 'List-item',
            4: 'Page-footer',
            5: 'Page-header',
            6: 'Picture',
            7: 'Section-header',
            8: 'Table',
            9: 'Text',
            10: 'Title'}

label2id = {'Caption': 0,
            'Footnote': 1,
            'Formula': 2,
            'List-item': 3,
            'Page-footer': 4,
            'Page-header': 5,
            'Picture': 6,
            'Section-header': 7,
            'Table': 8,
            'Text': 9,
            'Title': 10}


def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)

    # Remove ignored index (special tokens)
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]

    results = metric.compute(predictions=true_predictions, references=true_labels)
    if return_entity_level_metrics:
        # Unpack nested dictionaries
        final_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                for n, v in value.items():
                    final_results[f"{key}_{n}"] = v
            else:
                final_results[key] = value
        return final_results
    else:
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', type=str, choices=['small', 'base', 'large'], required=True, help='doclaynet dataset size')
    parser.add_argument('-s', '--step', type=int, default=500, help='max steps')
    parser.add_argument('-b', '--batch', type=int, default=8, help='batch size')
    parser.add_argument('-lr', '--learning_rate', type=float, default=1e-5, help='learning rate')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    return_entity_level_metrics = False
    train_dataset, eval_dataset = prepare_doclaynet("small")
    metric = load_metric("seqeval", trust_remote_code=True)
    processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base",
                                                            id2label=id2label,
                                                            label2id=label2id)

    training_args = TrainingArguments(output_dir="./model",
                                    max_steps=args.step,
                                    per_device_train_batch_size=args.batch,
                                    per_device_eval_batch_size=args.batch,
                                    learning_rate=args.learning_rate,
                                    eval_strategy="steps",
                                    eval_steps=100,
                                    save_steps=100,
                                    save_total_limit=2,
                                    load_best_model_at_end=True,
                                    metric_for_best_model="f1")

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=processor,
        data_collator=default_data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.evaluate()