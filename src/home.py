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

# ファイルの存在を確認
if not os.path.exists(filepath):
    st.error(f"{filepath} が存在しません。")
    exit()

# H1見出し
st.markdown("# ホーム")

df, food_list = sort_expiration(filepath = filepath, limit=3)

dt_now = datetime.datetime.now()
date = dt_now.strftime("%Y%m%d")

notice_df = df[df['expiration_date'] <= int(date)]

notice_df['expiration_date'] = pd.to_datetime(notice_df['expiration_date'].astype(str))
notice_df['expiration_date'] = notice_df['expiration_date'].dt.date

if len(notice_df) ==0:
    expanded = False
    comment = "賞味期限が近いものはありません"
else:
    expanded = True
    comment = "賞味期限が近いまたは過ぎているものがあります"

with st.expander(comment,expanded=expanded):
    st.dataframe(notice_df.loc[:,["food_name","expiration_date","amount" ]],hide_index=True)

## グラフの描画
# ランダムな表データ作成（ダミー）
data = np.random.rand(50,2)
# データフレーム作成
df = pd.DataFrame(data, columns=["サンプル1","サンプル2"])

# H3見出し
st.markdown("### 廃棄金額")
# グラフをアプリ上に表示
# 折れ線グラフ
st.line_chart(data=df,                     # データソース
              x="サンプル1",               # X軸
              y="サンプル2",               # Y軸
              width=0,                     # 表示設定（幅）
              height=0,                    # 表示設定（高さ）
              use_container_width=True,    # True の場合、グラフの幅を列の幅に設定
              )
# 面グラフ
st.area_chart(data=df,                     # データソース
              x="サンプル1",               # X軸
              y="サンプル2",               # Y軸
              width=0,                     # 表示設定（幅）
              height=0,                    # 表示設定（高さ）
              use_container_width=True,    # True の場合、グラフの幅を列の幅に設定
              )
# 棒グラフ
st.bar_chart(data=df,                      # データソース
              x="サンプル1",               # X軸
              y="サンプル2",               # Y軸
              width=0,                     # 表示設定（幅）
              height=0,                    # 表示設定（高さ）
              use_container_width=True,    # True の場合、グラフの幅を列の幅に設定
              )
