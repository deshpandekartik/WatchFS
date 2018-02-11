import sqlite3

class sqlite_database:
	
	conn = sqlite3.connect('database/watchfs.db')

	def initialize(self):
		# create database if not exist
		
		# create all tables , if not exist	
		self.conn.execute('''CREATE TABLE if not exists datamap (nodeid text, path text,  mode text, uid text, gid text, size text, timestamp text)''')

		self.conn.execute('''CREATE TABLE if not exists extensioncount (nodeid text, extension text,  count text)''')

		self.conn.execute('''CREATE TABLE if not exists notification (nodeid text, textualdata text, timestamp text)''')

		# commit the database
		self.commit_database()

	def execute_query(self, query):

		# Execute the query
		self.conn.execute(query)

		# commit the database
                self.commit_database()
		

	def get_row_count(self, query):
		# Execute the query
                cursor = self.conn.execute(query)

		count = cursor.fetchall()

                # commit the database
                self.commit_database()

		return count
		
	def fetch_data(self,query):

		cur = self.conn.cursor()
		cur.execute(query)
		rows = cur.fetchall()

		for row in rows:
			return row[0]

	def commit_database(self):
		self.conn.commit()	
