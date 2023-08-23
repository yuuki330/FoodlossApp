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

food_list = ['にんじん', 'じゃがいも', 'たまねぎ']
items_list = suggest_recipes(food_list=food_list)
for v in items_list:
    (_, recipeTitle, recipeMaterial, foodImageUrl, recipeUrl) = v
    print(recipeTitle, recipeMaterial, foodImageUrl, recipeUrl)

"""
失敗しない☆簡単肉じゃが♡4ステップのみ ['牛こま切れ', 'にんじん', 'じゃがいも', 'たまねぎ', 'しらたき', 'サラダ油', 'ーーーーーーーーーーーーーーーーーーー', '水', '醤油', 'みりん・砂糖・酒', 'ほんだしの素'] https://image.space.rakuten.co.jp/d/strg/ctrl/3/404ccfdd95a2c2b9e6ad9806ef798747a72fee0e.61.2.3.2.jpg https://recipe.rakuten.co.jp/recipe/1030006104/
離乳食後期から♪簡単クリームシチュー ['鶏むね肉', 'にんじん', 'たまねぎ', 'じゃがいも', 'バター', '小麦粉', '牛乳', '赤ちゃん用コンソメ', '塩'] https://image.space.rakuten.co.jp/d/strg/ctrl/3/d38ff29b0c9643e2e4af2d9e7d9ce8482f0d1032.68.9.3.3.jpg https://recipe.rakuten.co.jp/recipe/1350021304/
やわらか鶏むね肉でクリームシチュー ['鶏むね肉', '酒', '片栗粉', '塩コショウ', 'にんじん', 'たまねぎ', 'じゃがいも', '水', '牛乳', '市販のクリームシチューのルー'] https://image.space.rakuten.co.jp/d/strg/ctrl/3/cc561a70fb272073e68f3a994d9055398cac4384.63.9.3.3.jpg https://recipe.rakuten.co.jp/recipe/1650019267/
"""