from pydantic import BaseModel
import sqlite3
from database import SessionDep
from sqlmodel import select
from models import UserBase

class UserRepo():
    @staticmethod
    def get_user_by_id(user_id: int, session : SessionDep) -> UserBase:
        # with sqlite3.connect("my_data.db") as connection_my:
        #     cursor = connection_my.cursor()
        #     cursor.execute('SELECT id, name, password FROM USERS WHERE id = ?', (user_id,))
        #     result = cursor.fetchall()
        user = session.get(UserBase, user_id)
        return user
    

    @staticmethod
    def get_all_users(user_id: int, session : SessionDep):
        # with sqlite3.connect("my_data.db") as connection_my:
        #     cursor = connection_my.cursor()
        #     cursor.execute('SELECT id, name, password FROM USERS')
        #     result = cursor.fetchall()
        stat = select(UserBase)

        return session.exec(stat)

    @staticmethod
    def add_user(name, password, session : SessionDep):
        # result=0
        # with sqlite3.connect("my_data.db") as connection_my:
        #     cursor = connection_my.cursor()
        #     cursor.execute("INSERT INTO USERS (name, password) VALUES (?, ?)", (name, password))
        #     result = cursor.fetchall()
        user = UserBase(name=name, password=password)
        session.add(user)
        session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id):
        result = 0
        with sqlite3.connect("my_data.db") as connection_my:
            cursor = connection_my.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchall()
        return result
    
    @staticmethod
    def update_user_name(user_id, name):
        result = 0 
        with sqlite3.connect("my_data.db") as connection_my:
            cursor = connection_my.cursor()
            cursor.execute("UPDATE USERS SET name = ? WHERE id = ? ", (name, user_id))
            result = cursor.fetchall()
        return result
