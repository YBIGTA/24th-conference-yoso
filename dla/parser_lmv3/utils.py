import numpy as np 
from PIL import Image
import layoutparser as lp
import os
import re

def extract_title_bboxes(layout_result):
    title_bboxes = []
    for layout_block in layout_result:
        if layout_block.type == 'Title':
            title_bboxes.append(layout_block.block.coordinates)
    if len(title_bboxes) == 0:
        return "0"
    else:
        x1, y1, x2, y2 = title_bboxes[0][0], title_bboxes[0][1], title_bboxes[0][2], title_bboxes[0][3]
        bboxes=[x1, y1, x2, y2]
        # bbox에 해당하는 이미지 추출

        return bboxes

def title(image, bboxes):
    
    if bboxes == "0":
        return "NAN"
    else:
        title_bboxes = bboxes
        x1, y1, x2, y2 = title_bboxes[0], title_bboxes[1], title_bboxes[2], title_bboxes[3]
        segment_image = np.asarray(image)[int(y1):int(y2), int(x1):int(x2)]
        segment_image_pil = Image.fromarray(segment_image)
        ocr_agent = lp.TesseractAgent(languages='eng')
        title = ocr_agent.detect(segment_image_pil)
        title = re.sub(r'[\x00-\x1F\x7F]', ' ', title)
        return title

def sort_layout_by_columns(layout, threshold: float):
    left = []
    right = []
    for i in range(len(layout)):
        if layout[i].block.x_1 > threshold and layout[i].block.x_2 > threshold:
            right.append(layout[i])
        elif layout[i].block.x_1 < threshold and layout[i].block.x_2 < threshold:
            left.append(layout[i])
        else:
            left.append(layout[i])
    left_sorted = sorted(left, key=lambda blk: (blk.block.y_1, blk.block.x_1))
    right_sorted = sorted(right, key=lambda blk: (blk.block.y_1, blk.block.x_1))
    
    sorted_layout = lp.Layout()
    sorted_layout.extend(left_sorted)
    sorted_layout.extend(right_sorted)
    
    return sorted_layout


def extract_bboxes(layout_result):
    bboxes = []
    
    for layout_block in layout_result:
        x1, y1, x2, y2 = layout_block.block.coordinates[0], layout_block.block.coordinates[1], layout_block.block.coordinates[2], layout_block.block.coordinates[3]
        bbox=[x1, y1, x2, y2]
        bboxes.append(bbox)
    return bboxes
    
def OCR(image, layout_result):
    texts=[]
    for layout_block in layout_result:
        x1, y1, x2, y2 = layout_block.block.coordinates[0], layout_block.block.coordinates[1], layout_block.block.coordinates[2], layout_block.block.coordinates[3]
        bboxes=[x1, y1, x2, y2]
        segment_image = np.asarray(image)[int(y1):int(y2), int(x1):int(x2)]
        segment_image_pil = Image.fromarray(segment_image)
        ocr_agent = lp.TesseractAgent(languages='eng')
        if layout_block.type == "Figure":
            texts.append(f'{segment_image_pil}')
        else:
            text = ocr_agent.detect(segment_image_pil)
            text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)
            texts.append(text)
    
    return texts


def unnormalize_box(bbox, width, height):
     return [
         width * (bbox[0] / 1000),
         height * (bbox[1] / 1000),
         width * (bbox[2] / 1000),
         height * (bbox[3] / 1000),
     ]

def normalize(examples):
    
    coco_width = examples['width']
    coco_height = examples['height']
    
    normalized_bboxes = []
    ## bboxes_block가 비어 있는지 확인해봅시다.
    if examples['bboxes']:    
        for bbox in examples['bboxes']:
		        ## (x,y,w,h) -> (x,y,x+w,y+h)
		        ## 가끔 음수가 뜨기도 해서 max(0,val) 적용해줍니다.
            x1 = max(0,bbox[0])
            y1 = max(0,bbox[1])
            x2 = max(0,bbox[2])
            y2 = max(0,bbox[3])

            normalized_bbox = [
                int(np.rint(x1 / coco_width * 1000)),
                int(np.rint(y1 / coco_height * 1000)),
                int(np.rint(x2 / coco_width * 1000)),
                int(np.rint(y2 / coco_height * 1000))
            ]
            
            normalized_bboxes.append(normalized_bbox)
    return {
        "bboxes": normalized_bboxes,
        "texts" : examples["texts"],
        "height" : examples["height"],
        "width" : examples["width"]
    }