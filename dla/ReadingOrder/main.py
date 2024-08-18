import json
import argparse
from transformers import LayoutLMv3ForTokenClassification
from v3.helpers import prepare_inputs, boxes2inputs, parse_logits
from functools import cache
import time

@cache
def call_model(model_path):
    return LayoutLMv3ForTokenClassification.from_pretrained(model_path)
    

def normalize_box(bbox: list):
    return [int(bbox[0] / 10), int(bbox[1] / 10), int(bbox[2] / 10), int(bbox[3] / 10)]

def reorder_elements(elements, boxes, model_path):
    # Load the pre-trained model
    model = call_model(model_path)
    # Prepare model inputs
    inputs = boxes2inputs(boxes)
    inputs = prepare_inputs(inputs, model)

    # Get the logits from the model
    logits = model(**inputs).logits.cpu().squeeze(0)

    # Parse the logits to determine the order
    orders = parse_logits(logits, len(boxes))

    ordered_elements = [None] * len(orders)
    # Reorder elements according to the predicted order
    for i in range(len(orders)):
        temp = orders.index(i)
        elements[temp]['id'] = i
        ordered_elements[i] = elements[temp]

    return ordered_elements

def process_json(input_json_path, output_json_path, model_path):
    # Load JSON data
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    ordered_data = []
    elements = data['elements']
    bbox_temporal = []
    element_temporal = []
    current_page = elements[0]['page'] if elements else None

    for element in elements:
        page = element['page']

        left = min([point['x'] for point in element['bounding_box']])
        top = min([point['y'] for point in element['bounding_box']])
        right = max([point['x'] for point in element['bounding_box']])
        bottom = max([point['y'] for point in element['bounding_box']])
        normalized_bbox = normalize_box([left, top, right, bottom])

        if page == current_page:
            bbox_temporal.append(normalized_bbox)
            element_temporal.append(element)
        else:
            page_ordered = reorder_elements(element_temporal, bbox_temporal, model_path)
            ordered_data.extend(page_ordered)

            current_page = page
            bbox_temporal = [normalized_bbox]
            element_temporal = [element]

    if bbox_temporal and element_temporal:
        page_ordered = reorder_elements(element_temporal, bbox_temporal, model_path)
        ordered_data.extend(page_ordered)

    # Replace the original elements with the reordered ones
    data['elements'] = ordered_data

    # Save the reordered JSON back to a file (or use as needed)
    with open(output_json_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Reordered JSON elements saved to {output_json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reorder JSON elements based on LayoutLMv3 model.")
    parser.add_argument("input_json_path", type=str, help="Path to the input JSON file.")
    parser.add_argument("output_json_path", type=str, help="Path to save the reordered JSON file.")
    parser.add_argument("model_path", type=str, help='Model path haha')
    args = parser.parse_args()

    process_json(args.input_json_path, args.output_json_path, args.model_path)
    
