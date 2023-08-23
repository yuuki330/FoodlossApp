import streamlit as st
from typing import List
import sqlite3 

def suggest_recipes(food_list: List[str]) -> List[tuple[str, str, str, str, str]]:
    conn = sqlite3.connect("recipe.db")
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

st.markdown("# レシピ検索")
recipe_title_list = []
recipe_url_list = []
recipe_img_url_list = []

food_list = ['にんじん', 'じゃがいも', 'たまねぎ']
items_list = suggest_recipes(food_list=food_list)
for v in items_list:
    (_, recipeTitle, recipeMaterial, foodImageUrl, recipeUrl) = v
    # print(recipeTitle, recipeMaterial, foodImageUrl, recipeUrl)
    recipe_title_list.append(recipeTitle)
    recipe_url_list.append(recipeUrl)
    recipe_img_url_list.append(foodImageUrl)

print(recipe_title_list[0])
for i in range(len(recipe_title_list)):
    recipe = '<a href="' + str(recipe_url_list[i]) + '" target="_blank";style="font-family:monospace; color:cyan; font-size: 15px;">' + str(recipe_title_list[i]) + '</a>'
    recipe_img = '<img src="' + str(recipe_img_url_list[i]) + '" height="100" width="200">'
    st.components.v1.html("<center>" + recipe + "</center>" + "<center>" + recipe_img + "</center>")
    # st.components.v1.html("<center>" + recipe + "</center>")
    # st.components.v1.html(recipe_img)


