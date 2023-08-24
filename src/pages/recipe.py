import streamlit as st
from typing import List
import sqlite3
import pandas as pd
import os
import sys 
sys.path.append("../")

# 現在のスクリプトファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
# 1つ上の階層のディレクトリパスを取得
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
#"stock.sqlite"のディレクトリパスを取得
filepath = os.path.join(parent_dir, "stock_japanese.sqlite")

def _suggest_recipes(food_list: List[str]) -> List[tuple[str, str, str, str, str]]:
    try:
        with sqlite3.connect("recipe.db") as conn:
            cur = conn.cursor()

            execute_order = "SELECT * FROM recipe WHERE "
            sub_order = []
            for i in range(len(food_list)):
                if i:
                    execute_order += " AND "
                execute_order += "recipeMaterial LIKE ?"
                sub_order.append('%' + food_list[i] + '%')
            sub_order = tuple(sub_order)

            cur.execute(execute_order, sub_order)
            items_list = cur.fetchall()

        return items_list
    except sqlite3.Error as e:
        st.error(f"SQLite error: {e}")
        return []

## ソート系
# 期限切れ早い順にソート(pandasのdf形式) ＆ 食材上位3つ(list形式)
def sort_expiration(filepath = "stock.sqlite", limit=3):
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    sql = f"SELECT * FROM stocks ORDER BY expiration_date LIMIT {limit};"
    df = pd.read_sql(sql, conn)
    
    food_list = df.iloc[:,1].values.tolist()
    
    return df,food_list

def suggest_recipe(db_name="stock.sqlite"):
    _, food_list = sort_expiration(db_name)
    return _suggest_recipes(food_list)


## streamlit表示
st.markdown("# レシピ検索")
food_list = ['にんじん', 'じゃがいも', 'たまねぎ']
items_list = suggest_recipe(filepath)

for v in items_list:
    (_, recipeTitle, recipeMaterial, foodImageUrl, recipeUrl) = v

    recipe = f'<a href="{recipeUrl}" target="_blank" style="font-family:monospace; color:cyan; font-size: 15px;">{recipeTitle}</a>'
    recipe_img = f'<img src="{foodImageUrl}" height="100" width="200">'
    st.components.v1.html(f"<center>{recipe}</center><center>{recipe_img}</center>")

