import streamlit as st
import sqlite3
import os
import pandas as pd
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

import datetime
dt_now = datetime.datetime.now()

from functions import init_stock, add_stock, delete_stock, consume, discard,count_discard, get_stock, update_stock

# 現在のスクリプトファイルのディレクトリを取得
# current_dir = os.getcwd()
current_dir = os.path.dirname(os.path.abspath(__file__))
#"stock.sqlite"のディレクトリパスを取得
filepath = os.path.join(current_dir, "pages", "data", "stock.sqlite")

# ファイルの存在を確認
if not os.path.exists(filepath):
    st.error(f"{filepath} が存在しません。")
    exit()

st.title("Stock 画面")

with sqlite3.connect(filepath) as conn:
    sql = "SELECT * FROM stocks"
    df = pd.read_sql(sql, conn)


gd = GridOptionsBuilder.from_dataframe(df)
#gd.configure_selection(selection_mode='multiple', use_checkbox=True)
gd.configure_selection(selection_mode='single', use_checkbox=True)
gridoptions = gd.build()

grid_table = AgGrid(df, height=250, gridOptions=gridoptions,fit_columns_on_grid_load=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED)

selected_row = grid_table["selected_rows"]


amount =0

if len(selected_row) > 0:
    item_id = selected_row[0]["item_id"]
    amount = selected_row[0]["amount"]


date = dt_now.strftime("%Y%m%d")

col1, col2, col3, col4 = st.columns((1, 2, 1, 2))

with col1:
    consumption_amount = st.number_input('消費量', min_value=0, max_value=amount, value=0)

with col2:
    if st.button('消費'):
        if len(selected_row) > 0:
            #st.write("item id",item_id,"消費量",consumption_amount,"消費日",date)
            consume(item_id, date, consumption_amount, filepath)
            delete_stock(filepath)
            st.experimental_rerun()

with col3:
    discard_amount = st.number_input('廃棄量', min_value=0, max_value=amount, value=amount)

with col4:
    if st.button('廃棄'):
        if len(selected_row) > 0:
            #st.write("item id",item_id,"廃棄量",discard_amount,"廃棄日",date)
            discard(item_id, date, discard_amount, filepath)
            delete_stock(filepath)
            st.experimental_rerun()


col5, col6, = st.columns((1, 1))

with col5:

    with st.form("追加"):
        st.write("追加")
        food_name = st.text_input("食品名")
        expiration_date = st.date_input("消費期限", value=datetime.date(dt_now.year, dt_now.month, dt_now.day))
        expiration_date = expiration_date.strftime("%Y%m%d")
        purchase_date = st.date_input("購入日",  value=datetime.date(dt_now.year, dt_now.month, dt_now.day))
        purchase_date = purchase_date.strftime("%Y%m%d")
        price = st.number_input("値段",min_value=0)
        amount = st.number_input("量",min_value=0)

        # Every form must have a submit button.
        submitted = st.form_submit_button("追加")
        if submitted:
            st.write(food_name, expiration_date, purchase_date, price, amount)
            print(food_name, expiration_date, purchase_date, price, amount)
            add_stock(food_name, expiration_date, purchase_date, price, amount, filepath)
            st.experimental_rerun()

with col6:
    with st.form("変更"):
        if len(selected_row) > 0:
            #print("id",selected_row[0]["item_id"])
            item_id2= selected_row[0]["item_id"]
            item_info = get_stock(item_id2)
            print(item_info)
            st.write("変更")
            food_name2 = st.text_input("食品名",value=item_info[1])

            #print(type(item_info[2]))
            item_exp_date = datetime.datetime.strptime(str(item_info[2]),'%Y%m%d')
            #print(item_exp_date)
            expiration_date2 = st.date_input("消費期限", value=datetime.date(item_exp_date.year, item_exp_date.month, item_exp_date.day))
            expiration_date2 = expiration_date2.strftime("%Y%m%d")

            item_pur_date = datetime.datetime.strptime(str(item_info[3]),'%Y%m%d')
            purchase_date2 = st.date_input("購入日",  value=datetime.date(item_pur_date.year, item_pur_date.month, item_pur_date.day))
            purchase_date2 = purchase_date2.strftime("%Y%m%d")

            price2 = st.number_input("値段",min_value=0,value=item_info[4])
            amount2 = st.number_input("量",min_value=0,value=item_info[5])

            # Every form must have a submit button.
            submitted = st.form_submit_button("変更")
            if submitted:
                st.write(food_name, expiration_date, purchase_date, price, amount)
                print(food_name, expiration_date, purchase_date, price, amount)
                update_stock(item_id2,food_name2, expiration_date2, purchase_date2, price2, amount2, filepath)
                st.experimental_rerun()