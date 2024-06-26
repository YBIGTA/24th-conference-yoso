# Layout



# Parser+Lmv3
```
!apt update # vessl시 torch 2.0.0 이상
!apt install poppler-utils
!apt install tesseract-ocr
!pip install layoutparser
!pip install "detectron2@git+https://github.com/facebookresearch/detectron2.git@v0.5#egg=detectron2"
!pip install pdf2img
!pip install "layoutparser[ocr]"
!pip uninstall google-cloud-vision google-api-core google-cloud-storage
!pip install google-cloud-vision google-api-core google-cloud-storage
!pip install opencv-python==4.8.0.74
```
model.zip google-drive에서 다운로드
```
mkdir model
unzip model.zip -d ./model
```
```
python main.py
```
