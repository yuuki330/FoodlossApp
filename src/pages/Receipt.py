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
#"stock.sqlite"のディレクトリパスを取得
# stock_path = os.path.join(current_dir, "data", "stock.sqlite")
stock_path = st.session_state.user_db_filepath

def get_expiration_limit(food_name, filepath = expiration_path):
    import sqlite3
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()

    cur.execute("SELECT expiration FROM food WHERE food_name = ?",(food_name, ))
    items = cur.fetchone()

    return items # like (180, 0) or None


st.title("レシート読み込み")

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

        # gd = GridOptionsBuilder.from_dataframe(df)
        # #gd.configure_selection(selection_mode='multiple', use_checkbox=True)
        # gd.configure_selection(selection_mode='single', use_checkbox=True)
        # gridoptions = gd.build()

        # grid_table = AgGrid(df, height=250, gridOptions=gridoptions,fit_columns_on_grid_load=True,
        #                     update_mode=GridUpdateMode.SELECTION_CHANGED)

        # selected_row = grid_table["selected_rows"]
        with st.form("登録"):
            # import sys 
            # sys.path.append("../")
            # from functions import init_stock, add_stock, delete_stock, consume, discard,count_discard, get_stock, update_stock
        
            # # 現在のスクリプトファイルのディレクトリを取得
            # current_dir = os.path.dirname(os.path.abspath(__file__))
            # # 1つ上の階層のディレクトリパスを取得
            # parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
            # #"stock.sqlite"のディレクトリパスを取得
            # filepath = os.path.join(parent_dir, "stock.sqlite")
        
            st.write("編集")
            exp_date = []
            pur_date = []
            for i in range(df.shape[0]):
                col1, col2, col3, col4, col5 = st.columns((1, 1, 1, 1, 1))
                with col1:
                    df.iloc[i,0] = st.text_input("食品名",value=df.iloc[i,0],key=f"food{i}")
                with col2:
                    exp_date.append(datetime.datetime.strptime(str(df.iloc[i,1]),'%Y%m%d'))
                    df.iloc[i,1] = st.date_input("消費期限", value=datetime.date(exp_date[i].year, exp_date[i].month, exp_date[i].day),key=f"exp{i}")
                    df.iloc[i,1] = df.iloc[i,1].strftime("%Y%m%d")
                with col3:
                    pur_date.append(datetime.datetime.strptime(str(df.iloc[i,2]),'%Y%m%d'))
                    df.iloc[i,2] = st.date_input("購入日", value=datetime.date(pur_date[i].year, pur_date[i].month, pur_date[i].day),key=f"pur{i}")
                    df.iloc[i,2] = df.iloc[i,2].strftime("%Y%m%d")
                with col4:
                    df.iloc[i,3] = st.number_input("値段",min_value=0,value=int(df.iloc[i,3]), key=f"price{i}")
                with col5:
                    df.iloc[i,4] = st.number_input("量",min_value=0,value= df.iloc[i,4].item(), key=f"amount{i}")
        
            #st.write(df)
            submitted3 = st.form_submit_button("追加")
        
            if submitted3:
                st.write("追加")
                print(df)
                for i in range(df.shape[0]):
                    add_stock(str(df.iloc[i,0]), int(df.iloc[i,1]), int(df.iloc[i,2]), int(df.iloc[i,3]), int(df.iloc[i,4].item()), stock_path)
                    print(f"add{i}")
        
                st.experimental_rerun()
