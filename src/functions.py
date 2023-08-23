import sqlite3
import os
import pandas as pd

## DB操作系
# stocksテーブル、discardテーブル、consumeテーブルを初期化
def init_stock(filepath = "stock.sqlite"):

    if os.path.exists(filepath):
        os.remove(filepath)
    conn = sqlite3.connect(filepath) 

    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS items")

    # Stocks Table stocksテーブルの主キーは自動振り分け
    cur.execute("""CREATE TABLE stocks(
        item_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        food_name TEXT,
        expiration_date DATE,
        purchase_date DATE,
        price INTEGER,
        amount INTEGER
    )""")

    # Consumed Table
    cur.execute("""CREATE TABLE consumed(
        item_id INTEGER PRIMARY KEY,
        food_name TEXT,
        expiration_date DATE,
        purchase_date DATE,
        price INTEGER,
        amount INTEGER,
        consumed_date DATE
    )""")

    # Discard Table
    cur.execute("""CREATE TABLE discard(
        item_id INTEGER PRIMARY KEY,
        food_name TEXT,
        expiration_date DATE,
        purchase_date DATE,
        price INTEGER,
        amount INTEGER,
        discard_date DATE
    )""")
    
    conn.commit()


def add_stock(food, exp_date, pur_date, price, amount, filepath = "stock.sqlite"):
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    cur.execute('INSERT INTO stocks(food_name, expiration_date, purchase_date, price, amount) values(?, ?, ?, ?, ?);',(food, exp_date, pur_date, price, amount))
    
    conn.commit()

def update_stock(item_id, food, exp_date, pur_date, price, amount, filepath = "stock.sqlite"):
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    
    cur.execute('UPDATE stocks set food_name=?, expiration_date=?, purchase_date=?, price=?, amount=? WHERE item_id=?;',(food, exp_date, pur_date, price, amount, item_id))
    
    conn.commit()
    

def delete_stock(filepath = "stock.sqlite"): # amountが0のレコードを削除
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    cur.execute("DELETE FROM stocks WHERE amount <= 0")
    
    conn.commit()
    
def get_stock(item_id, filepath = "stock.sqlite"):
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM stocks WHERE item_id = ?", (item_id, ))
    stock = cur.fetchone()
    
    return list(stock)

def consume(item_id, consumed_date, consumed_amount, filepath = "stock.sqlite"):
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM stocks WHERE item_id = ?", (item_id, ))
    stock = cur.fetchone()

    food_name = stock[1]
    exp_date = stock[2]
    pur_date = stock[3]
    price = stock[4]
    prev_amount = stock[5]

    # 消費テーブルに既に存在するか調べる
    cur.execute("SELECT * FROM consumed WHERE item_id = ?", (item_id, ))
    consumed_item = cur.fetchone()
    

    # consumedテーブルに消費量ぶん追加
    if consumed_item == None: # まだdiscardテーブルにidが存在しないとき
        cur.execute('INSERT INTO consumed values(?, ?, ?, ?, ?, ?, ?)', (item_id,food_name,exp_date,pur_date,price,consumed_amount,consumed_date ))
    else:
        new_amount = consumed_item[5] + consumed_amount
        cur.execute("UPDATE consumed set amount = ?, consumed_date = ? where item_id = ?", (new_amount, consumed_date ,item_id))
        
    # stackテーブルの該当レコードのamountを消費量分減少
    new_amount = prev_amount - consumed_amount
    cur.execute("UPDATE stocks set amount = ? where item_id = ?", (new_amount, item_id))

    conn.commit()
    

def discard(item_id, discard_date, discard_amount, filepath = "stock.sqlite"):
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()

    cur.execute("SELECT * FROM stocks WHERE item_id = ?", (item_id, ))
    stock = cur.fetchone()

    food_name = stock[1]
    exp_date = stock[2]
    pur_date = stock[3]
    price = stock[4]
    prev_amount = stock[5]

    # 廃棄テーブルに既に存在するか調べる
    cur.execute("SELECT * FROM discard WHERE item_id = ?", (item_id, ))
    discard_item = cur.fetchone()

    # 廃棄テーブルに消費量ぶん追加
    if discard_item == None: # まだdiscardテーブルにidが存在しないとき
        cur.execute('INSERT INTO discard values(?, ?, ?, ?, ?, ?, ?)', (item_id,food_name,exp_date,pur_date,price,discard_amount,discard_date ))
    else:
        new_amount = discard_item[5] + discard_amount
        cur.execute("UPDATE discard set amount = ?, discard_date = ? where item_id = ?", (new_amount, discard_date ,item_id))
        
    # 在庫テーブルの該当レコードのamountを消費量分減少
    new_amount = prev_amount - discard_amount
    cur.execute("UPDATE stocks set amount = ? where item_id = ?", (new_amount, item_id))

    conn.commit()

## カウント系
# 廃棄金額カウント関数
def count_discard(start_date, end_date, filepath = "stock.sqlite"):
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    cur.execute("SELECT price, amount FROM discard WHERE discard_date BETWEEN ? AND ?",(start_date,end_date))
    items = cur.fetchall()
    #print(items)
    
    discard_sum = 0
    for price,amount in items:
        discard_sum += price*amount
    
    return discard_sum

# 購入金額カウント（未完成）
def count_stock(filepath = "stock.sqlite"):
    
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    cur.execute("SELECT price, amount FROM stocks")
    items = cur.fetchall()
    #print(items)
    
    purchase_sum = 0
    for price,amount in items:
        purchase_sum += price*amount
    
    return purchase_sum


## ソート系
# 期限切れ早い順にソート(pandasのdf形式) ＆ 食材上位3つ(list形式)
def sort_expiration(filepath = "stock.sqlite", limit=3):
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    sql = f"SELECT * FROM stocks ORDER BY expiration_date LIMIT {limit};"
    df = pd.read_sql(sql, conn)
    
    food_list = df.iloc[:,1].values.tolist()
    
    return df,food_list

# 購入日順にソート(pandasのdf形式) ＆ 食材上位3つ(list形式)
def sort_purchase(filepath = "stock.sqlite", limit=3):
    conn = sqlite3.connect(filepath) 
    cur = conn.cursor()
    
    sql = f"SELECT * FROM stocks ORDER BY purchase_date DESC LIMIT {limit};"
    df = pd.read_sql(sql, conn)
    
    food_list = df.iloc[:,1].values.tolist()
    
    return df,food_list


"""
# 構文メモ
cur.execute('INSERT INTO stocks values(1, "apple", "20230830", "20230820", 100, 3);')
cur.execute('INSERT INTO stocks values(2, "orange", "20230821", "20230820", 100, 2);')
conn.commit()

with sqlite3.connect(filepath) as conn:
        sql = "SELECT * FROM stocks"
        df = pd.read_sql(sql, conn)
        print(df)
        
# print food before expiration dates
today = "20230822"
cur.execute("SELECT * FROM stocks WHERE expiration_date <= ?", (today, ))
items_list = cur.fetchall()
print(items_list)
print()

# delete food before expiration dates
cur.execute("DELETE FROM stocks WHERE expiration_date <= ?", (today, ))
cur.execute("SELECT * FROM stocks")
items_list = cur.fetchall()
print(items_list)
print()

# update food amount
count = 2
food = "apple"
cur.execute("UPDATE stocks set amount = ? where food_name = ?", (count, food))
cur.execute("SELECT * FROM stocks")
items_list = cur.fetchall()
print(items_list)
print()
"""