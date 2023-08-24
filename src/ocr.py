from google.cloud import vision
import io
import os
import cv2
from enum import Enum
import re
from typing import List
import matplotlib.pyplot as plt
from preprocess import get_food_and_price_list
from google.cloud.vision_v1 import types

# Vision APIのキー
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./rakuten-intern-396705-196bcfd5bb92.json"

def get_vision_api_response(input_file: str):
    # レシートのパス
    # input_file = "./receipt2.jpeg"

    # APIへのイニシエーション
    client = vision.ImageAnnotatorClient()
    with io.open(input_file, 'rb') as image_file:
        content = image_file.read()

    # bytes化した写真データをAPIに送る
    image = vision.Image(content=content)

    # OCRの結果を受け取る
    response = client.document_text_detection(image=image)

    return response

def get_sorted_lines(response) -> List[str]:
    document = response.full_text_annotation
    bounds = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        x = symbol.bounding_box.vertices[0].x
                        y = symbol.bounding_box.vertices[0].y
                        text = symbol.text
                        bounds.append([x, y, text, symbol.bounding_box])
    bounds.sort(key=lambda x: x[1])
    old_y = -1
    line = []
    lines = []
    threshold = 1
    for bound in bounds:
        x = bound[0]
        y = bound[1]
        if old_y == -1:
            old_y = y
        elif old_y-threshold <= y <= old_y+threshold:
            old_y = y
        else:
            old_y = -1
            line.sort(key=lambda x: x[0])
            lines.append(line)
            line = []
        line.append(bound)
    line.sort(key=lambda x: x[0])
    lines.append(line)
    return lines

# 商品名と値段を一行にまとめる
def get_food_and_price(lines: List[str]) -> str:
    if_append_text = False
    texts = []
    for line in lines:
        text = [i[2] for i in line]
        text = ''.join(text)
        if '合計' in text:
            if_append_text = False

        if if_append_text:
            texts.append(text)

        if '領収書' in text:
            if_append_text = True
    
    return ''.join(texts)

def ocr(input_file: str) -> List[str]:
    response = get_vision_api_response(input_file)

    lines = get_sorted_lines(response)

    return get_food_and_price(lines)