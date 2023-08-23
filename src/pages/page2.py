import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr import ocr
from preprocess import get_food_and_price_list
from pathlib import Path
import tempfile

st.title("page2")

uploaded_file = st.file_uploader("レシート画像をアップロード", type=['jpg','png'])

if uploaded_file is not None:
    img=Image.open(uploaded_file)
    img_array = np.array(img)
    st.image(img_array,caption = 'アップロード画像', use_column_width = True)

    # Make temp file path from uploaded file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        fp = Path(tmp_file.name)
        fp.write_bytes(uploaded_file.getvalue())
        food_price_str = ocr(fp)
        df = pd.DataFrame(get_food_and_price_list(food_price_str),columns=['Name','Price'])
        st.table(df)
