import sqlite3


conn = sqlite3.connect('database/watchfs.db')
conn.execute('''drop table notification''')
