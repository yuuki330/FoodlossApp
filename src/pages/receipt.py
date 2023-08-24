import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from ocr import ocr
from preprocess import get_food_and_price_list
from pathlib import Path
import tempfile

import os
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from functions import add_stock
import datetime
today = datetime.date.today()

# 現在のスクリプトファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
#"expiration.db"のディレクトリパスを取得
expiration_path = os.path.join(current_dir, "data", "expiration.db")

def get_expiration_limit(food_name, filepath = expiration_path):
    import sqlite3
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()

    cur.execute("SELECT expiration FROM food WHERE food_name = ?",(food_name, ))
    items = cur.fetchone()

    return items # like (180, 0) or None


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
        df = pd.DataFrame(get_food_and_price_list(food_price_str),columns=['food_name','price'])
        # st.table(df)
        
        df["purchase_date"] = today.strftime("%Y%m%d")
        df["amount"] = 1

        df["expiration_date"] = today.strftime("%Y%m%d")
        for i in range(len(df)):
            food_name = df.iloc[i]["food_name"]
            expiration_limit = get_expiration_limit(food_name)
            if expiration_limit is not None:
                df.loc[i, "expiration_date"] = (today + datetime.timedelta(days=expiration_limit[0])).strftime("%Y%m%d")
    
        df = df.reindex(columns=['food_name', 'expiration_date', 'purchase_date', 'price', 'amount'])

        gd = GridOptionsBuilder.from_dataframe(df)
        #gd.configure_selection(selection_mode='multiple', use_checkbox=True)
        gd.configure_selection(selection_mode='single', use_checkbox=True)
        gridoptions = gd.build()

        grid_table = AgGrid(df, height=250, gridOptions=gridoptions,fit_columns_on_grid_load=True,
                            update_mode=GridUpdateMode.SELECTION_CHANGED)

        selected_row = grid_table["selected_rows"]
