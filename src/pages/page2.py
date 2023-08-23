import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr import ocr
from preprocess import get_food_and_price_list

st.title("page2")

img_path = st.file_uploader("ファイルアップロード", type=['jpg','png']) # ファイルアップロード
img=Image.open(img_path)
img_array = np.array(img)
st.image(img_array,caption = 'アップロード画像', use_column_width = True)

food_price_str = ocr(img_path)
df = pd.DataFrame(get_food_and_price_list(food_price_str),columns=['Name','Price'])

st.table(df)