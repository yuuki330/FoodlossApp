import sqlite3
import os
import pandas as pd

filepath = "stock.sqlite"
if os.path.exists(filepath):
    os.remove(filepath)
conn = sqlite3.connect(filepath) 

cur = conn.cursor()
cur.execute("DROP TABLE IF EXISTS items")

# Stock Table
cur.execute("""CREATE TABLE stocks(
    item_id INTEGER PRIMARY KEY,
    food_name TEXT,
    expiration_date DATE,
    purchase_date DATE,
    price INTEGER,
    amount INTEGER
)""")

cur.execute('INSERT INTO stocks values(1, "apple", "20230830", "20230820", 100, 3);')
cur.execute('INSERT INTO stocks values(2, "orange", "20230821", "20230820", 100, 2);')
conn.commit()

with sqlite3.connect(filepath) as conn:
    sql = "SELECT * FROM stocks"
    df = pd.read_sql(sql, conn)
    print(df)

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



"""
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