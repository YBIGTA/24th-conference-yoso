import numpy as np
import layoutparser as lp
import pdf2image
from utils import *
import os
import re
import json

def process_pdf_to_text_dict(pdf_path):
    # PDF를 이미지로 변환
    img = np.asarray(pdf2image.convert_from_path(pdf_path)[0])
    model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_X_101_32x8d_FPN_3x/config',
                                 extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5],
                                 label_map={0: "Text", 1: "Title", 2: "List", 3:"Table", 4:"Figure"})
    # 텍스트 감지 및 레이아웃 감지 수행
    layout_result = model.detect(img)
    cols = img.shape[1]
    layout_result = sort_layout_by_columns(layout_result, threshold = cols//2)

    # 타이틀 텍스트 추출
    title_bboxes = extract_title_bboxes(layout_result)
    if title_bboxes == "0":
        title_result = "NAN"
    else:
        title_result = title(img, title_bboxes)
    title_result = re.sub(r'[\x00-\x1F\x7F]', ' ', title_result)
    
    # 고유 ID 생성
    file_name = os.path.basename(pdf_path)
    
    # 결과를 딕셔너리 형태로 반환
    return {
        "id": file_name,
        "text": title_result
    }

def extract_titles_from_directory(directory):
    results = []
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            result = process_pdf_to_text_dict(pdf_path)
            results.append(result)
    return results

def save_results_to_json(results, output_path):
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4)

pdf_directory = "data/paper_pdf"  

# 결과를 저장할 JSON 파일 경로
output_json_path = "title.json"  

# 디렉토리에서 타이틀 추출 후 JSON 파일로 저장
results = extract_titles_from_directory(pdf_directory)
save_results_to_json(results, output_json_path)
