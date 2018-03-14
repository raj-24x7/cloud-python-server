#!/usr/bin/python

import MySQLdb
import time
import datetime
import configure

def main():
	# Open database connection
	#db = MySQLdb.connect("172.31.76.68","cloud-user","mnnitcloud","cloud" )
	db_username = configure.get_db_username()
	db_password = configure.get_db_password()
	db_host = configure.get_db_host()
	db_name = configure.get_db_name()

	db = MySQLdb.connect(db_host,db_username,db_password,db_name)
	
	# prepare a cursor object using cursor() method
	cursor = db.cursor()
	print("hello")

	# Prepare SQL query to DELETE required records
	sql = "SELECT * FROM VMdetails;"

	# Execute the SQL command
	cursor.execute(sql)

	results = cursor.fetchall()
	db.close()
	db = MySQLdb.connect(db_host,db_username,db_password,db_name)


	for row in results:
		vmname=row[3]
		doe=row[8]
		s=str(doe)   
		temp=time.mktime(datetime.datetime.strptime(s, "%Y-%m-%d").timetuple())
		com=time.time()

		if(com>=temp) :
			cur=db.cursor()
			try:
				print(vmname)
				cur.execute("update VMdetails set status='deactive' where VM_name='%s' " %(vmname))
				db.commit()
			except:
				print("error")
	db.close()

if __name__=="__main__":
	main()