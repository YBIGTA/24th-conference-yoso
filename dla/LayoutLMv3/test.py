import io
from PIL import Image

from Inference import categorize


bboxes = [
    [135, 80, 475, 122],
    [166, 176, 282, 215],
    [77, 128, 207, 167],
    [247, 129, 364, 167],
    [419, 129, 523, 166],
    [336, 175, 440, 211],
    [52, 220, 114, 232],
    [52, 234, 298, 444],
    [52, 451, 137, 465],
    [52, 467, 297, 492],
    [51, 498, 118, 511],
    [50, 514, 302, 711],
    [14, 217, 37, 564],
    [319, 217, 554, 364],
    [319, 368, 431, 388],
    [446, 367, 557, 388],
    [349, 399, 525, 413],
    [315, 441, 424, 456],
    [315, 458, 562, 712]
 ]

texts = [
    "LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking",   # Title
    "Yupan Huang∗\nSun Yat-sen University\nhuangyp28@mail2.sysu.edu.cn",   # Text 1
    "Tengchao Lv\nMicrosoft Research Asia\ntengchaolv@microsoft.com",   # Text 2
    "Lei Cui\nMicrosoft Research Asia\nlecu@microsoft.com",   # Text 3
    "Yutong Lu\nSun Yat-sen University\nluyutong@mail.sysu.edu.cn",   # Text 4
    "Furu Wei\nMicrosoft Research Asia\nfuwei@microsoft.com",   # Text 5
    "ABSTRACT",    # Section-header 1
    "Self-supervised pre-training techniques have achieved remarkable progress in Document AI.",   # Text 6
    "CCS CONCEPTS",    # Section-header 2
    "Applied computing → Document analysis; • Computing methodologies → Natural language processing.",   # Text 7
    "KEYWORDS",    # Section-header 3
    "document ai, layoutlm, multimodal pre-training, vision-and-language ACM Reference Format:Yupan Huang, Tengchao Lv, Lei Cui, Yutong Lu, and Furu Wei. 2022.",   # Text 8
    "arXiv:2204.08387v3 [cs.CL] 19 Jul 2022",     # Page-footer
    "picture picture picture picture picture",   # Picture
    "(a) Text-centric form under- standing on FUNSD",   # Caption 1
    "(b)Image-centriclayoutanal- ysis on PubLayNet",   # Caption 2
    "Figure 1: Examples of Document AI Tasks.",   # Caption 3
    "1 INTRODUCTION",   # Section-header 4
    "In recent years, pre-training techniques have been making waves in the Document AI community by achieving remarkable progress on document understanding tasks [2, 13–15, 17, 25, 28, 31, 32, 40, 41, 50, 52, 54–56]."    # Text 9
]

image = Image.open("../2204.08387v3.jpg")
img_byte_arr = io.BytesIO()
image.save(img_byte_arr, format='PNG')
img_byte_arr.seek(0)  # Move to the beginning of the BytesIO object
image = Image.open(img_byte_arr)

output = categorize("./model/checkpoint-100", image, bboxes, texts)
print(output)