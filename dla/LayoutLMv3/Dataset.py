## Python imports
import numpy as np
from collections import defaultdict
## Huggingface imports
from transformers import AutoProcessor
from datasets import load_dataset, Features, Sequence, Value, Array2D, Array3D


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


## Load doclayNet dataset from huggingface.
## small: pierreguillou/DocLayNet-small (about 1% of DocLayNet) < 1.000k document images (691 train, 64 val, 49 test)
## base : pierreguillou/DocLayNet-base  (about 10% of DocLayNet) < 10.000k document images (6910 train, 648 val, 499 test)
## large: pierreguillou/DocLayNet-large (about 100% of DocLayNet) < 100.000k document images (69.103 train, 6.480 val, 4.994 test)
def load_doclaynet(size : str):
    
    if size not in ['small','base','large']:
        return None
    
    dataset_path = 'pierreguillou/DocLayNet-' + size
    dataset = load_dataset(dataset_path, trust_remote_code=True)
    dataset = dataset.filter(lambda example: example["doc_category"] == "scientific_articles")
    return dataset


## Preprocess dolcaynet dataset before entering LayoutLMv3Processor.
## 1. Remove data with empty bounding boxes.
## 2. Adjust bounding box coordinates (x, y, w, h) -> (x, y, x+w, y+h).
## 3. Normalize bounding box coordinates into values between 0 to 1000.
## 4. Concatenate all texts within the same bounding boxes.
def preprocess_doclaynet(examples):
    normalized_bboxes = []
    bbox_to_texts = defaultdict(list)
    bbox_to_category = defaultdict(list)

    if examples['bboxes_block']:    
        for text, bbox, category in zip(examples['texts'], examples['bboxes_block'], examples['categories']):
            x1 = max(0, bbox[0])
            y1 = max(0, bbox[1])
            x2 = max(0, bbox[0] + bbox[2])
            y2 = max(0, bbox[1] + bbox[3])

            normalized_bbox = (
                int(np.rint(x1 / 1025 * 1000)),
                int(np.rint(y1 / 1025 * 1000)),
                int(np.rint(x2 / 1025 * 1000)),
                int(np.rint(y2 / 1025 * 1000))
            )

            bbox_to_texts[normalized_bbox].append(text)
            bbox_to_category[normalized_bbox].append(category)

    concatenated_texts = []
    concatenated_categories = []

    for bbox, texts in bbox_to_texts.items():
        concatenated_texts.append(' '.join(texts))
        concatenated_categories.append(bbox_to_category[bbox][0])
        normalized_bboxes.append(list(bbox))

    preprocessed_example = {
        'id': examples['id'],
        'texts': concatenated_texts,
        'bboxes_block': normalized_bboxes,
        'categories': concatenated_categories,
        'image': examples['image'],
        'page_hash': examples['page_hash'],
        'original_filename': examples['original_filename'],
        'page_no': examples['page_no'],
        'num_pages': examples['num_pages'],
        'original_width': examples['original_width'],
        'original_height': examples['original_height'],
        'coco_width': examples['coco_width'],
        'coco_height': examples['coco_height'],
        'collection': examples['collection'],
        'doc_category': examples['doc_category']
    }
    return preprocessed_example


## Produce encodings using the processor for each examples in the dataset.
def encode(examples):
    images = examples["image"]
    words  = examples["texts"]
    boxes  = examples["bboxes_block"]
    word_labels = examples["categories"]

    processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    encoding = processor(images, words, boxes=boxes, word_labels=word_labels,
                        truncation=True, padding="max_length")
    return encoding


## Load, proprocess, and encode doclaynet dataset.
def prepare_doclaynet(size):
    
    print("Loading dataset from huggingface...")
    dataset = load_doclaynet(size)

    print("Preprocessing dataset...")
    dataset = dataset = dataset.map(preprocess_doclaynet, remove_columns=dataset['train'].column_names)
    dataset = dataset.filter(lambda x: x["bboxes_block"] != [])

    features = Features({
        'pixel_values': Array3D(dtype="float32", shape=(3, 224, 224)),
        'input_ids': Sequence(feature=Value(dtype='int64')),
        'attention_mask': Sequence(Value(dtype='int64')),
        'bbox': Array2D(dtype="int64", shape=(512, 4)),
        'labels': Sequence(feature=Value(dtype='int64')),
    })
    column_names = dataset["train"].column_names

    print("Encoding train dataset...")
    train_dataset = dataset["train"].map(
        encode,
        batched=True,
        remove_columns=column_names,
        features=features,
    )
    train_dataset.set_format("torch")

    print("Encoding evalidation dataset...")
    eval_dataset = dataset["validation"].map(
        encode,
        batched=True,
        remove_columns=column_names,
        features=features,
    )
    eval_dataset.set_format("torch")
    return train_dataset, eval_dataset