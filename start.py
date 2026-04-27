import sqlite3

connection_my = sqlite3.connect("my_data.db")



cursor = connection_my.cursor()


#cursor.execute('''DROP TABLE NEWS ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS NEWS(
id INTEGER PRIMARY KEY,
news_lable TEXT NOT NULL,
content TEXT NOT NULL,
age INTEGER               
               
               ) 
               
               ''')

news_data = [
    ('Технологии', 'Новый смартфон представлен', 15),
    ('Наука', 'Открыта новая планета', 7),
    ('Экономика', 'Курс валют вырос', 40),
    ('Спорт', 'Хоккейный матч перенесен', 5)
]

cursor.execute("""
    INSERT INTO NEWS (news_lable, content, age) 
    VALUES (?, ?, ?)
""", news_data)

connection_my.commit()

connection_my.close()