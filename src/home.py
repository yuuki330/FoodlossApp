import streamlit as st
import pandas as pd
import numpy as np

recipe1 = '<a href="https://recipe.rakuten.co.jp/recipe/1790017077/" style="font-family:monospace; color:cyan; font-size: 15px;">魚屋さんが教えてくれた カレイの煮付け</a>'
recipe1_img = '<img src="https://image.space.rakuten.co.jp/d/strg/ctrl/3/862cd72bae056544418aba5cf0e0dc34ebeeb1d9.15.9.3.3.jpg" height="100" width="200">'
st.components.v1.html("<center>" + recipe1 + "</center>" + "<center>" + recipe1_img + "</center>")

tmp = st.slider("slider", 0, 100, 50)
st.text(tmp)

dataframe = pd.DataFrame(np.arange(12).reshape(3, 4),
                  columns=['col_0', 'col_1', 'col_2', 'col_3'],
                  index=['row_0', 'row_1', 'row_2'])
dataframe.iloc[1, 2] = tmp
st.dataframe(dataframe) # pandasのデータフレーム
