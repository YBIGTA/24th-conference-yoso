# LayoutReader Model - Extended Version
## Background

We have successfully trained the LayoutReader model (https://github.com/ppaanngggg/layoutreader). 
Initially, LayoutReader was only capable of reading horizontal textual information. 
However, our team has now extended its functionality by generating a custom dataset from academic papers and their LaTeX sources. 
As a result, the model can now also read vertical information, specifically in documents such as research papers.

## How to use
we have model path folder in https://drive.google.com/drive/u/0/folders/1_cZYpoa967cggNL8EnNCzk1BKdzsFKyY

download it to your environment.

	git clone https://github.com/prodong04/you-only-search-once.git
	cd you-only-search-once/dla/ReadingOrder

## inference
	python main.py ./AI_VIT_O_0.json ./reordered.json ./checkpoint-320

This command requires three arguments:
python main.py input_json_path output_json_path model_path
input_json_path: The path to your input JSON file containing the document layout.
output_json_path: The path where the output JSON with the reordered layout will be saved.
model_path: The path to the model checkpoint you downloaded earlier.
