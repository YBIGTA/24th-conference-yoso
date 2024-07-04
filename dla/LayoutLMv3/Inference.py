## Python imports
import io
import torch
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngImageFile
## Huggingface imports
from transformers import AutoProcessor
from transformers import AutoModelForTokenClassification


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


def normalize_box(bbox, width, height):
     return [
         int(np.rint(1000 * (bbox[0] / width))),
         int(np.rint(1000 * (bbox[1] / height))),
         int(np.rint(1000 * (bbox[2] / width))),
         int(np.rint(1000 * (bbox[3] / height))),
     ]


def unnormalize_box(bbox, width, height):
     return [
         int(np.rint(width * (bbox[0] / 1000))),
         int(np.rint(height * (bbox[1] / 1000))),
         int(np.rint(width * (bbox[2] / 1000))),
         int(np.rint(height * (bbox[3] / 1000))),
     ]

def categorize(model_dir, image, bboxes, texts):
    processor =  AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)

    assert isinstance(image, PngImageFile)
    img_width = image.width
    img_height = image.height
    normalized_bboxes = [normalize_box(box, img_width, img_height) for box in bboxes]

    encoding = processor(images=image,
                         text=texts,
                         boxes=normalized_bboxes,
                         return_offsets_mapping=True,
                         return_tensors="pt",
                         truncation=True,
                         padding="max_length")
    offset_mapping = encoding.pop('offset_mapping')

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    encoding.to(device)
    outputs = model(**encoding)

    predictions = outputs.logits.argmax(-1).squeeze().tolist()
    token_boxes = encoding.bbox.squeeze().tolist()

    is_subword = np.array(offset_mapping.squeeze().tolist())[:,0] != 0
    true_predictions = [id2label[pred] for idx, pred in enumerate(predictions) if not is_subword[idx]]
    true_boxes = [unnormalize_box(box, img_width, img_height) for idx, box in enumerate(token_boxes) if not is_subword[idx]]
    output = [(text, bbox) for text, bbox in zip(true_predictions, true_boxes) if bbox != [0, 0, 0, 0]]
    return output