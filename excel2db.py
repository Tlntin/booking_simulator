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
df2 = pd.merge(df2, df1[["电报码", "经度", "纬度"]], left_on="起点", right_on="电报码", how="left")
df2 = pd.merge(df2, df1[["电报码", "经度", "纬度"]], left_on="终点", right_on="电报码", how="left")
df2 = df2.reset_index()
_ = df2.pop("index")
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
    type INTEGER NOT NULL,
    second_class_price INTEGER,
    first_class_price INTEGER,
    business_class_price INTEGER,
    no_seat_price INTEGER,
    hard_seat_price INTEGER,
    hard_sleeper_price INTEGER,
    soft_sleeper_price INTEGER
);
'''
cursor.execute(create_sql2)
new_data_list = []
for i in range(len(df2)):
    trips_type = int(df2.loc[i, "类别"])
    x1 = df2.loc[i, "经度_x"]
    x2 = df2.loc[i, "经度_y"]
    y1 = df2.loc[i, "纬度_x"]
    y2 = df2.loc[i, "纬度_y"]
    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    # 对于高铁
    if trips_type == 1:
        # 二等座
        price1 = round(distance * 55)
        # 一等座
        price2 = round(price1 * 1.6)
        # 商务座
        price3 = round(price1 * 3.15)
        # 无座/硬座/硬卧/软卧
        price4 = price5 = price6 = price7 = None
    # 对于普铁
    else:
        # 二等座/一等座/商务座
        price1 = price2 = price3 = None
        # 无座/硬座
        price4 = price5 = round(distance * 15)
        # 硬卧
        price6 = round(distance * 25)
        # 软卧
        price7 = round(distance * 43)
    code = df2.loc[i, "车次"]
    station_from = df2.loc[i, "起点"]
    station_to = df2.loc[i, "终点"]
    start = df2.loc[i, "出发时间"]
    end = df2.loc[i, "到达时间"]
    data = [
        code, station_from, station_to, start, end, trips_type,
        price1, price2, price3, price4, price5, price6, price7
    ]
    new_data_list.append(data)

insert_sql2 = '''
INSERT INTO trips(
    code,
    station_from,
    station_to,
    start,
    end,
    type,
    second_class_price,
    first_class_price,
    business_class_price,
    no_seat_price,
    hard_seat_price,
    hard_sleeper_price,
    soft_sleeper_price
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
'''
cursor.executemany(insert_sql2, new_data_list)
db.commit()



