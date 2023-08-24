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
        df["expiration_date"] = "20230823"
        df["amount"] = 1
        df = df.reindex(columns=['food_name', 'expiration_date', 'purchase_date', 'price', 'amount'])

        gd = GridOptionsBuilder.from_dataframe(df)
        #gd.configure_selection(selection_mode='multiple', use_checkbox=True)
        gd.configure_selection(selection_mode='single', use_checkbox=True)
        gridoptions = gd.build()

        grid_table = AgGrid(df, height=250, gridOptions=gridoptions,fit_columns_on_grid_load=True,
                            update_mode=GridUpdateMode.SELECTION_CHANGED)

        selected_row = grid_table["selected_rows"]