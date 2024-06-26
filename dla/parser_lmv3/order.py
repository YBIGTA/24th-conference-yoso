from transformers import LayoutLMv3ForTokenClassification
from helpers import prepare_inputs, boxes2inputs, parse_logits
from utils import normalize_order
import pdf2image
import cv2
import numpy as np

model = LayoutLMv3ForTokenClassification.from_pretrained("hantian/layoutreader")

# list of [left, top, right, bottom], bboxes of spans, should be range from 0 to 1000
boxes = [[188, 226, 1531, 287], 
 [180, 317, 1565, 774], 
 [192, 778, 278, 808], 
 [651, 789, 1534, 1045], 
 [197, 837, 618, 930], 
 [188, 965, 633, 1328], 
 [658, 1178, 1549, 1293], 
 [638, 1312, 1575, 2001], 
 [192, 1365, 625, 1899], 
 [192, 1940, 602, 2030], 
 [180, 317, 1565, 774], 
 [651, 789, 1534, 1045], 
 [638, 1312, 1575, 2001]]

width, height = 1653, 2173
noramlize_boxes = normalize_order(boxes, width, height)
inputs = boxes2inputs(noramlize_boxes)
inputs = prepare_inputs(inputs, model)
logits = model(**inputs).logits.cpu().squeeze(0)
orders = parse_logits(logits, len(boxes))



boxes = [boxes[i] for i in orders]
# draw boxes
pdf_path = 'f05a34e7-5c90-453c-981b-b46a9644964b.pdf'
pil_images = pdf2image.convert_from_path(pdf_path)
opencv_images = [cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR) for pil_img in pil_images]

img = opencv_images[2]

for idx, box in enumerate(boxes):
    x0, y0, x1, y1 = box
    x0 = round(x0)
    y0 = round(y0)
    x1 = round(x1)
    y1 = round(y1)
    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 0, 255), 1)
    cv2.putText(
        img,
        str(idx),
        (x1, y1),
        cv2.FONT_HERSHEY_PLAIN,
        0.5,
        (0, 0, 255),
        1,
    )
output_img_path = 'annotated_image.png'
cv2.imwrite(output_img_path, img)

# [0, 1, 2, ...]