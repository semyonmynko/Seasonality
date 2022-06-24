import csv, sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

with open('KC-057.csv','r') as fin:
    # csv.DictReader по умолчанию использует первую строку под заголовки столбцов
    dr = csv.DictReader(fin, delimiter=",")
    to_db = [(i['code'], i['date'], i['num_1'], i['num_2'], i['num_3'], i['num_4']) for i in dr]

cur.executemany("INSERT INTO db (code, data_, num_1, num_2, num_3, num_4) VALUES (?, ?, ?, ?, ?, ?);", to_db)

connection.commit()
connection.close()