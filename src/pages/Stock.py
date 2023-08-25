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
current_dir = os.path.dirname(os.path.abspath(__file__))
#"stock.sqlite"のディレクトリパスを取得
# filepath = os.path.join(current_dir, "data", "stock.sqlite")
filepath = st.session_state.user_db_filepath

# ファイルの存在を確認
if not os.path.exists(filepath):
    print(f"{filepath} が存在しません。")
    exit()

st.title("在庫一覧")

with sqlite3.connect(filepath) as conn:
    sql = "SELECT * FROM stocks"
    df = pd.read_sql(sql, conn)

# item_id列をデータフレームの最後に移動
cols = list(df.columns)
cols.remove('item_id')
df = df[cols + ['item_id']]
cols = df.columns.tolist()
food_name_index = cols.index('food_name')
amount_index = cols.index('amount')
cols.insert(food_name_index + 1, cols.pop(amount_index))
price_index = cols.index('price')
cols.insert(food_name_index + 2, cols.pop(price_index))
df = df[cols]

df["expiration_date"] = df["expiration_date"].astype(str)
df["purchase_date"] = df["purchase_date"].astype(str)

for i in range(len(df)):
    df["expiration_date"][i] = str(df["expiration_date"][i][:4]) +"/"+str(df["expiration_date"][i][4:6]) + "/" + str(df["expiration_date"][i][6:])
    df["purchase_date"][i] = str(df["purchase_date"][i][:4]) +"/"+str(df["purchase_date"][i][4:6]) + "/" + str(df["purchase_date"][i][6:])
    df["price"][i] = str(df["price"][i]) + "円"

df = df.sort_values('item_id', ascending=False)

gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_selection(selection_mode='single', use_checkbox=False)
gd.configure_column("item_id", hide=True)  # item_idを非表示に設定
gd.configure_column("food_name", headerName="食材", width=180) 
gd.configure_column("amount", headerName="数量[個]", width=100)
gd.configure_column("price", headerName="価格", width=100)
gd.configure_column("expiration_date", headerName="消費期限")
gd.configure_column("purchase_date", headerName="購入日")
gd.configure_default_column(min_column_width=110)
gridoptions = gd.build()

grid_table = AgGrid(df, height=250, gridOptions=gridoptions,fit_columns_on_grid_load=True,
                    update_mode=GridUpdateMode.SELECTION_CHANGED)

selected_row = grid_table["selected_rows"]

amount =0

if len(selected_row) > 0:
    item_id = selected_row[0]["item_id"]
    amount = selected_row[0]["amount"]
    selected_row[0]["price"] = int(selected_row[0]["price"].replace("円",""))

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

if len(selected_row) == 0:
    initial = 0
else:
    initial = 1

selector=st.radio( "",["追加","変更"],horizontal =True,index =initial)

if selector == "追加":

    with st.form("追加"):
        st.write("追加")
        food_name = st.text_input("食品名")
        expiration_date = st.date_input("消費期限", value=datetime.date(dt_now.year, dt_now.month, dt_now.day))
        expiration_date = expiration_date.strftime("%Y%m%d")
        purchase_date = st.date_input("購入日",  value=datetime.date(dt_now.year, dt_now.month, dt_now.day))
        purchase_date = purchase_date.strftime("%Y%m%d")
        price = st.number_input("値段[円]",min_value=0)
        amount = st.number_input("数量[個]",min_value=0)

        # Every form must have a submit button.
        submitted = st.form_submit_button("追加")
        if submitted:
            st.write(food_name, expiration_date, purchase_date, price, amount)
            print(food_name, expiration_date, purchase_date, price, amount)
            add_stock(food_name, expiration_date, purchase_date, price, amount, filepath)
            st.experimental_rerun()

else:
    if len(selected_row) > 0:
        with st.form("変更"):
            item_id2= selected_row[0]["item_id"]
            item_info = get_stock(item_id2, filepath)
            print(item_info)
            st.write("変更")
            food_name2 = st.text_input("食品名",value=item_info[1])

            item_exp_date = datetime.datetime.strptime(str(item_info[2]),'%Y%m%d')
            expiration_date2 = st.date_input("消費期限", value=datetime.date(item_exp_date.year, item_exp_date.month, item_exp_date.day))
            expiration_date2 = expiration_date2.strftime("%Y%m%d")

            item_pur_date = datetime.datetime.strptime(str(item_info[3]),'%Y%m%d')
            purchase_date2 = st.date_input("購入日",  value=datetime.date(item_pur_date.year, item_pur_date.month, item_pur_date.day))
            purchase_date2 = purchase_date2.strftime("%Y%m%d")

            price2 = st.number_input("値段[円]",min_value=0,value=item_info[4])
            amount2 = st.number_input("数量[個]",min_value=0,value=item_info[5])

            # Every form must have a submit button.
            submitted = st.form_submit_button("変更")
            if submitted:
                st.write("変更",food_name2, expiration_date2, purchase_date2, price2, amount)
                print(food_name2, expiration_date2, purchase_date2, price2, amount)
                update_stock(item_id2,food_name2, expiration_date2, purchase_date2, price2, amount2, filepath)
                st.experimental_rerun()