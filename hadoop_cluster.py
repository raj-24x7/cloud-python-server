# Service Creation of Hadoop Clusters
#

import MySQLdb
from pexpect import pxssh
import configure

def getDBConnection():
	
	db_username = configure.get_db_username()
	db_password = configure.get_db_password()
	db_host = configure.get_db_host()
	db_name = configure.get_db_name()

	db=MySQLdb.connect(db_host,db_username,db_password,db_name)
	return db

def getCursor(db):
	cursor=db.cursor()
	return cursor

def count_ip(db):
	result=executeQuery(db,"SELECT COUNT(*) as count FROM `ip_pool` WHERE `status`!='allocated'")
	print(result[0][0])
	return result[0][0]

def executeQuery(db,query):
	cursor=getCursor(db)
	try:
		cursor.execute(query)
		result=cursor.fetchall()
		db.commit()
		return result
	except:
		print("error")
		db.rollback()

def getHypervisorConnection(db,dom0name):
	result=executeQuery(db,"SELECT * FROM `hypervisor` WHERE name='%s' "% (dom0name))
	print(result[0][1],result[0][2],result[0][3])
	try:
		s=pxssh.pxssh()
		s.login(result[0][1],result[0][2],result[0][3])
		return s
		#s.sendline()
		#s.prompt()
		#print (s.before)
	except :
		print ("pxssh failed on login.")
    	#print str(e)

def createHadoopCluster(db,dom0name ,name, ram, noofslaves, ips) :
	connection = getHypervisorConnection(db,dom0name);
	#print(connection)
	connection.sendline("ll")
	connection.prompt()
	print(connection.before.decode("UTF-8"))
	command = "bash ~/utilityScripts/createCluster.sh "+str(name)+" "+str(ram)+" "+str(noofslaves);

	for i in range(noofslaves+1) :
		command = command+" "+ips[i];
		

	command = command+" "+"";
	print(command)
	connection.sendline(command)
	connection.prompt()





def main(post):
	db=getDBConnection()
	ip=[] 
	if(post['button']=="approve") :
		noofslaves=post['number_slave']
		if(count_ip(db)>=noofslaves+1):
			result=executeQuery(db,"SELECT `ip` FROM `ip_pool` WHERE `status`!='allocated'")			
			for i in range(noofslaves+1) :
				print(result[i][0])
				ip.append(result[i][0])
			createHadoopCluster(db,post['hypervisor_name'], post['hadoop_name'], post['ram'], noofslaves, ip)
			query = "UPDATE `hadoop` SET `status`='created' where hadoop_name='%s'" %post['hadoop_name']
			executeQuery(db,query)
			#sql="INSERT INTO VMdetails (username,VM_name) VAlUES ('%s','%s')" % (str(post['username']),str(post['hadoop_name']))
			#print(sql)
			#cursor=getCursor(db)
			#cursor.execute(sql)
			#cursor.commit()
			sql = "INSERT INTO VMdetails (username,VM_name,cpu,ram,storage,hypervisor_name,ip,doe,iscluster) VALUES ('%s','%s',%d,'%s','%s','%s','%s','%s','%s')" % (post['username'],post['hadoop_name']+"Master",int(post['cpu']),post['ram'],post['storage'],post['hypervisor_name'],ip[0],str(post['doe']),post['hadoop_name']	)
			print("fhsudhff"+sql);
			#cursor=getCursor(db)
			#cursor.execute(sql)
			#cursor.commit()
			executeQuery(db,sql)

			#Slaves
			for i in range(1,noofslaves+1):
				VM_name = post['hadoop_name']+"Slave"+str(i)
				sql ="INSERT INTO VMdetails (username,VM_name,cpu,ram,storage,hypervisor_name,ip,doe,iscluster) VALUES ('%s','%s',%d,'%s','%s','%s','%s','%s','%s')" % (post['username'],VM_name,int(post['cpu']),post['ram'],post['storage'],post['hypervisor_name'],ip[i],str(post['doe']),post['hadoop_name'])
				executeQuery(db,sql)

			print("Updating IPs")
			for i in range(noofslaves+1):
				sql = "UPDATE ip_pool SET `status`='allocated' WHERE ip='%s'"%(str(ip[i]))
				executeQuery(db, sql)

	db.close()	


if __name__=="__main__":
	post = {
		"username": "admin",
		"hadoop_name": "trying",
		"description": "testing hadoop cluster",
		"number_slave": 2,
		"cpu": 2,
		"storage": "10GB",
		"ram": "256MB",
		"doe":"1995-8-25",
		"button":"approve" ,
		"hypervisor_name":"xenserver-trial" 
		}
	main(post)