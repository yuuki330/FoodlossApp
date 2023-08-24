import streamlit as st
import pandas as pd
import numpy as np

import datetime
dt_now = datetime.datetime.now()

from functions import sort_expiration

import os

# 現在のスクリプトファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
#"stock.sqlite"のディレクトリパスを取得
filepath = os.path.join(current_dir, "pages", "data", "stock.sqlite")

df, food_list = sort_expiration(filepath = filepath, limit=3)

dt_now = datetime.datetime.now()
date = dt_now.strftime("%Y%m%d")

#print("A",df)
#print("B",df[df['expiration_date'] <= int(date)])

notice_df = df[df['expiration_date'] <= int(date)]

notice_df['expiration_date'] = pd.to_datetime(notice_df['expiration_date'].astype(str))
notice_df['expiration_date'] = notice_df['expiration_date'].dt.date
#print("type",notice_df['expiration_date'].dtype)
#print(notice_df['expiration_date'] )

if len(notice_df) ==0:
    expanded = False
    comment = "賞味期限が近いものはありません"
else:
    expanded = True
    comment = "賞味期限が近いまたは過ぎているものがあります"

with st.expander(comment,expanded=expanded):
    
    st.dataframe(notice_df.loc[:,["food_name","expiration_date","amount" ]],hide_index=True)
