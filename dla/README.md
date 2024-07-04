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
# Reading Order
아직 모듈화가 진행되지 않음. 시험용으로 사용한 코드 업로드 함.
```
!pip install transformers
```
만 있으면 기존의 layout 환경에서 돌아갈 것.
https://github.com/ppaanngggg/layoutreader 참조
