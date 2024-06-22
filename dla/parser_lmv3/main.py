import numpy as np
import layoutparser as lp
import pdf2image
from utils import *
import os
import re
import json
from transformers import AutoModelForTokenClassification
from transformers import AutoProcessor
import torch

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




def layout_parser(img):
    model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                 extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                 label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    # 텍스트 감지 및 레이아웃 감지 수행
    img = np.asarray(img)
    layout_result = model.detect(img)
    width = img.shape[1]
    height = img.shape[0]
    layout_result = sort_layout_by_columns(layout_result, threshold = width//2)
    
    bboxes = extract_bboxes(layout_result)
    texts = OCR(img, layout_result)
    
    # 결과를 딕셔너리 형태로 반환
    return {
        "bboxes": bboxes,
        "texts": texts,
        "width": width,
        "height": height
    }

def lp_lmv3(pdf_path):
    images = pdf2image.convert_from_path(pdf_path)
    for img in images:  
        output = layout_parser(img)
        output = normalize(output)
        model = AutoModelForTokenClassification.from_pretrained("model/model/checkpoint-500")
        processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
        
        words = output["texts"]
        boxes = output["bboxes"]
        width = output["width"]
        height = output["height"]
        breakpoint()
        encoding = processor(img, words, boxes=boxes, return_offsets_mapping=True, return_tensors="pt",truncation=True, padding="max_length")
        offset_mapping = encoding.pop('offset_mapping')

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)
        encoding.to(device)
        outputs = model(**encoding)

        predictions = outputs.logits.argmax(-1).squeeze().tolist()
        token_boxes = encoding.bbox.squeeze().tolist()

        is_subword = np.array(offset_mapping.squeeze().tolist())[:,0] != 0
        true_predictions = [id2label[pred] for idx, pred in enumerate(predictions) if not is_subword[idx]]
        true_boxes = [unnormalize_box(box, width, height) for idx, box in enumerate(token_boxes) if not is_subword[idx]]
        output = [(text, bbox) for text, bbox in zip(true_predictions, true_boxes) if bbox != [0, 0, 0, 0]]
        breakpoint()

lp_lmv3("2204.08387v3.pdf")
        
