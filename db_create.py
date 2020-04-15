"""Create database"""
import sqlite3

from config import  ADMINS

connection = sqlite3.connect("botter.db", check_same_thread = True)
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS "users" (
	"id"	INTEGER,
	"city"	TEXT,
	"username"	TEXT,
	"status"	INTEGER,
	"hour"	INTEGER,
	"minute"	INTEGER
)""")
# ! Admin id is required
data_tuple = (ADMINS[0], "admin")
cursor.execute("INSERT INTO 'users'('id','username') VALUES(?,?);", data_tuple)
connection.commit()