"""
convert excel to sqlite db
"""
import pandas as pd
import sqlite3
import os

# excel get from https://github.com/metromancn/Parse12306/blob/master/output/%E5%85%A8%E5%9B%BD%E9%AB%98%E9%80%9F%E5%88%97%E8%BD%A6%E6%97%B6%E5%88%BB%E8%A1%A8_20160310.xlsx
excel_path = "./data/全国高速列车时刻表_20160310.xlsx"
db_path = "./data/sqlite.db"

# connect sqlite
db = sqlite3.connect(db_path)
cursor = db.cursor()

# get station
df1 = pd.read_excel(excel_path, sheet_name="车站")
print(df1.head(3))
# create table to save station
create_sql1 = '''
create table IF NOT EXISTS station(
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    pinyin TEXT NOT NULL,
    initial_pinyin TEXT NOT NULL,
    pinyin_code TEXT NOT NULL,
    longitude REAL NOT NULL,
    latitude REAL NOT NULL
)
'''
cursor.execute(create_sql1)
insert_sql1 = '''
INSERT INTO station VALUES(?, ?, ?, ?, ?, ?, ?, ?)
'''
cursor.executemany(insert_sql1, df1.values.tolist())
db.commit()

# --- get trips --- #
df2 = pd.read_excel(excel_path, sheet_name="车次")
df2["类别"] = df2["类别"].map({"动车": 0, "快速": 0, "高速": 1})
df2["出发时间"] = df2["出发时间"].apply(lambda x: x.strftime("%H:%d"))
df2["到达时间"] = df2["到达时间"].apply(lambda x: x.strftime("%H:%d"))
_ = df2.pop("服务")
print(df2.head(3))

create_sql2 = '''
create table IF NOT EXISTS trips(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    station_from TEXT NOT NULL,
    station_to TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    type INTEGER NOT NULL -- '0: ordinary; 1: high-speed;'
);
'''
cursor.execute(create_sql2)
# comment_sql2 = '''
# COMMENT ON TABLE trips.type IS '0: ordinary; 1: high-speed;'
# '''
# cursor.execute(comment_sql2)
insert_sql2 = '''
INSERT INTO trips(code, station_from, station_to, start, end, type)
VALUES (?, ?, ?, ?, ?, ?)
'''
cursor.executemany(insert_sql2, df2.values.tolist())
db.commit()



