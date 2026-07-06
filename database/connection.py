import sqlite3

DATABASE_NAME = 'database/database.db'

def connect_database():    
    return sqlite3.connect(DATABASE_NAME)