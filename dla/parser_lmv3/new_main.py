import numpy as np
import layoutparser as lp
import pdf2image
from PIL import Image, ImageDraw, ImageFont
import os
import re
import json
from transformers import AutoModelForTokenClassification, AutoProcessor
import torch
import argparse
import cv2

class DocumentProcessor:
    def __init__(self, pdf_path, model_path, result_path, visualize=False):
        self.pdf_path = pdf_path
        self.model_path = model_path
        self.result_path = result_path
        self.visualize = visualize
        self.pdf_id = os.path.splitext(os.path.basename(pdf_path))[0]
        self.label_list = ['Caption', 'Footnote', 'Formula', 'List-item', 'Page-footer', 'Page-header', 'Picture', 'Section-header', 'Table', 'Text', 'Title']
        self.id2label = {i: label for i, label in enumerate(self.label_list)}
        self.label2id = {label: i for i, label in enumerate(self.label_list)}
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.processor = AutoProcessor.from_pretrained("microsoft/layoutlmv3-base", apply_ocr=False)
    
    def sort_layout_by_columns(self, layout, threshold):
        left, right = [], []
        for block in layout:
            if block.block.x_1 > threshold and block.block.x_2 > threshold:
                right.append(block)
            else:
                left.append(block)
        left_sorted = sorted(left, key=lambda blk: (blk.block.y_1, blk.block.x_1))
        right_sorted = sorted(right, key=lambda blk: (blk.block.y_1, blk.block.x_1))
        sorted_layout = lp.Layout()
        sorted_layout.extend(left_sorted)
        sorted_layout.extend(right_sorted)
        return sorted_layout

    def extract_bboxes(self, layout_result):
        return [list(block.block.coordinates) for block in layout_result]
    
    def ocr(self, image, layout_result):
        texts = []
        for block in layout_result:
            x1, y1, x2, y2 = map(int, block.block.coordinates)
            segment_image = np.asarray(image)[y1:y2, x1:x2]
            segment_image_pil = Image.fromarray(segment_image)
            ocr_agent = lp.TesseractAgent(languages='eng')
            text = ocr_agent.detect(segment_image_pil) if block.type != "Figure" else f'{segment_image_pil}'
            text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)
            texts.append(text)
        return texts

    def unnormalize_box(self, bbox, width, height):
        return [
         width * (bbox[0] / 1000),
         height * (bbox[1] / 1000),
         width * (bbox[2] / 1000),
         height * (bbox[3] / 1000),
     ]
        
    def normalize(self, examples):
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

    def layout_parser(self, img):
        model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                         extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                         label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"})
        img_np = np.asarray(img)
        layout_result = model.detect(img_np)
        layout_result = self.sort_layout_by_columns(layout_result, threshold=img_np.shape[1] // 2)
        return {"bboxes": self.extract_bboxes(layout_result), "texts": self.ocr(img, layout_result), "width": img_np.shape[1], "height": img_np.shape[0]}
    
    def segment_image(self, img, output, page_number):
        ocr_result = []
        img_np = np.array(img)  # PIL 이미지를 NumPy 배열로 변환
        img_height, img_width = img_np.shape[:2]  # 이미지 크기 가져오기

        for id, (category, bbox) in enumerate(output):
            x1, y1, x2, y2 = map(int, bbox)
            
            # 바운딩 박스 좌표를 이미지 범위 내에 있도록 조정
            x1 = max(0, min(x1, img_width - 1))
            y1 = max(0, min(y1, img_height - 1))
            x2 = max(0, min(x2, img_width - 1))
            y2 = max(0, min(y2, img_height - 1))

            if x1 >= x2 or y1 >= y2:
                continue  # 바운딩 박스가 유효하지 않은 경우 건너뜀
            
            segment_image = img_np[y1:y2, x1:x2]
            segment_image_pil = Image.fromarray(segment_image)
            ocr_agent = lp.TesseractAgent(languages='eng')
            text = ocr_agent.detect(segment_image_pil)
            text = re.sub(r'[\x00-\x1F\x7F]', ' ', text)
            ocr_result.append((id, category, bbox, text))
            if category in ["Figure", "Table"]:
                save_path = os.path.join(self.result_path, "visualize", self.pdf_id, str(page_number))
                os.makedirs(save_path, exist_ok=True)
                segment_image_pil.save(os.path.join(save_path, f"{id}.png"))
        return ocr_result
    
    def visualize_image(self, img, output, page_number):
        img_np = np.array(img)  # PIL 이미지를 NumPy 배열로 변환
        img_height, img_width = img_np.shape[:2]  # 이미지 크기 가져오기

        category_colors = {
            "Text": (0, 255, 0), "Title": (255, 0, 0), "List": (0, 0, 255), "Table": (255, 255, 0),
            "Figure": (255, 0, 255), "Caption": (0, 255, 255), "Footnote": (128, 0, 128),
            "Formula": (128, 128, 0), "Page-footer": (0, 128, 128), "Page-header": (128, 0, 0),
            "Section-header": (0, 128, 0)
        }

        output_dir = os.path.join(self.result_path, "visualize", self.pdf_id)
        os.makedirs(output_dir, exist_ok=True)

        # PIL 이미지 객체 생성
        image = Image.fromarray(img_np)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        for category, bbox in output:
            x1, y1, x2, y2 = map(int, bbox)
            
            # 바운딩 박스 좌표를 이미지 범위 내에 있도록 조정
            x1 = max(0, min(x1, img_width - 1))
            y1 = max(0, min(y1, img_height - 1))
            x2 = max(0, min(x2, img_width - 1))
            y2 = max(0, min(y2, img_height - 1))

            if x1 >= x2 or y1 >= y2:
                continue  # 바운딩 박스가 유효하지 않은 경우 건너뜀
            
            color = category_colors.get(category, (255, 255, 255))  # Default to white if category not found
            draw.rectangle([x1, y1, x2, y2], outline=color)
            draw.text((x1 + 10, y1 - 10), category, fill=color, font=font)

        output_path = os.path.join(output_dir, f"{page_number}.png")
        image.save(output_path)
        
    def create_json_from_output(self, output):
        json_data = {"id": self.pdf_id, "elements": []}
        for page_number, page_output in enumerate(output):
            for id, category, bbox, text in page_output:
                json_data["elements"].append({
                    "bounding_box": [{"x": bbox[0], "y": bbox[1]}, {"x": bbox[2], "y": bbox[1]}, {"x": bbox[2], "y": bbox[3]}, {"x": bbox[0], "y": bbox[3]}],
                    "category": category,
                    "id": id,
                    "page": page_number + 1,
                    "text": text,
                })
        json_path = os.path.join(self.result_path, "json", f"{self.pdf_id}.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=4)

    def process(self):
        results = []
        images = pdf2image.convert_from_path(self.pdf_path)
        # print pd_id 
        print(f'PDF_ID: {self.pdf_id}')
        for page_number, img in enumerate(images):
            output = self.layout_parser(img)
            output = self.normalize(output)
            words, boxes = output["texts"], output["bboxes"]
            words = [word[:80] for word in words]
            width, height = output["width"], output["height"]
            encoding = self.processor(img, words, boxes=boxes, return_offsets_mapping=True, return_tensors="pt", truncation=True, padding="max_length")
            offset_mapping = encoding.pop('offset_mapping')
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model.to(device)
            encoding.to(device)
            outputs = self.model(**encoding)
            predictions = outputs.logits.argmax(-1).squeeze().tolist()
            token_boxes = encoding.bbox.squeeze().tolist()
            is_subword = np.array(offset_mapping.squeeze().tolist())[:, 0] != 0
            true_predictions = [self.id2label[pred] for idx, pred in enumerate(predictions) if not is_subword[idx]]
            true_boxes = [self.unnormalize_box(box, width, height) for idx, box in enumerate(token_boxes) if not is_subword[idx]]
            final_output = [(category, bbox) for category, bbox in zip(true_predictions, true_boxes) if bbox != [0, 0, 0, 0]]
            if self.visualize:
                self.visualize_image(img, final_output, page_number + 1)
            results.append(self.segment_image(img, final_output, page_number + 1))
        self.create_json_from_output(results)

def parse_args():
    parser = argparse.ArgumentParser(description='Layout Parser for LayoutLMv3')
    parser.add_argument('-p', '--pdf_path', type=str, default='/root/paper_pdf', help='Path to the PDF Directory')
    parser.add_argument('-m', '--model_path', type=str, required=True, help='Path to the Model Directory')
    parser.add_argument('-r', '--result_path', type=str, default='/root/result', help='Path to the Result Directory')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug Mode: Process only 5 PDF files')
    parser.add_argument('-v', '--visualize', action='store_true', help='Visualize Mode: Visualize the result of detection')
    return parser.parse_args()

def main():
    args = parse_args()
    
    pdf_directory = args.pdf_path
    model_path = args.model_path
    result_directory = args.result_path
    debug = args.debug
    visualize = args.visualize

    pdf_files = os.listdir(pdf_directory)
    if debug:
        pdf_files = pdf_files[:1]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_directory, pdf_file)
        if os.path.isfile(pdf_path) and pdf_file.endswith('.pdf'):
            processor = DocumentProcessor(pdf_path, model_path, result_directory, visualize)
            processor.process()

if __name__ == "__main__":
    main()
