import streamlit as st
from typing import List
import sqlite3
import pandas as pd
import os

# 現在のスクリプトファイルのディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
#"stock.sqlite"のディレクトリパスを取得
filepath = os.path.join(current_dir, "data", "stock.sqlite")
#"recipe.db"のディレクトリパスを取得
recipe_path = os.path.join(current_dir, "data", "recipe.db")

def _suggest_recipes(food_list: List[str]) -> List[tuple[str, str, str, str, str]]:
    try:
        with sqlite3.connect(recipe_path) as conn:
            cur = conn.cursor()

            execute_order = "SELECT * FROM recipe WHERE "
            sub_order = []
            for i in range(len(food_list)):
                if i:
                    execute_order += " OR "
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

def suggest_recipe(db_path="stock.sqlite"):
    _, food_list = sort_expiration(db_path)
    return _suggest_recipes(food_list)

# ファイルの存在を確認
if not os.path.exists(filepath):
    st.error(f"{filepath} が存在しません。")
elif not os.path.exists(recipe_path):
    st.error(f"{recipe_path} が存在しません。")
else:
    ## streamlit表示
    st.markdown("# レシピ提案")
    _, food_list = sort_expiration(filepath=filepath, limit=3)
    items_list = suggest_recipe(filepath)

    for v in items_list:
        (_, recipeTitle, recipeMaterial, foodImageUrl, recipeUrl) = v
        recipeMaterial = eval(recipeMaterial)
        initial_display = 3
        displayed_materials = recipeMaterial[:initial_display]
        hidden_materials = recipeMaterial[initial_display:]

        materials_html = '<ul style="font-family:monospace; color:white; font-size: 12px;">'
        for material in displayed_materials:
            # food_listに材料が存在する場合、太字で表示
            if material in food_list:
                materials_html += f'<li><strong>{material}</strong></li>'
            else:
                materials_html += f'<li>{material}</li>'

        hidden_items = ''
        if hidden_materials:
            for material in hidden_materials:
                # food_listに材料が存在する場合、太字で表示
                if material in food_list:
                    hidden_items += f'<li><strong>{material}</strong></li>'
                else:
                    hidden_items += f'<li>{material}</li>'

        # ボタンがクリックされたかどうかの状態を確認
        button_clicked = st.session_state.get(f"button_clicked_{recipeTitle}", False)

        # 初期の材料リストを定義
        material = materials_html

        if button_clicked:
            # ボタンがクリックされた場合、material変数を更新して隠れている材料を追加
            material += hidden_items

        material += '</ul>'

        # material変数に含まれるHTMLの<li>タグの数をカウント
        material_li_count = material.count('<li>')
        # 1つの<li>タグ項目の高さを設定
        height_per_li = 21
        # 必要な高さを計算
        calculated_height = material_li_count * height_per_li + 50

        recipe = f'<a href="{recipeUrl}" target="_blank" style="font-family:monospace; color:cyan; font-size: 13px;">{recipeTitle}</a>'
        combined_html = f"{recipe}<br>{material}"

        with st.container():
            col1, col2 = st.columns([1,1])
            with col1:
                st.components.v1.html(combined_html, height=calculated_height)
                
                # ボタンをHTMLの下に配置
                if hidden_materials and not button_clicked:
                    if st.button(f"もっと見る", key=recipeTitle):
                        st.session_state[f"button_clicked_{recipeTitle}"] = True
                        # ページを再読み込み
                        st.experimental_rerun()

            with col2:
                st.image(foodImageUrl, use_column_width = "auto")