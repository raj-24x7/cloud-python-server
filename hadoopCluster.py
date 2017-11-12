#
#

import MySQLdb
from pexpect import pxssh

def getDBConnection():
	db=MySQLdb.connect("localhost","root","robin","cloud")
	return db

def getCursor(db):
	cursor=db.cursor()
	return cursor


def count_ip(db):
	result=executeQuery(db,"SELECT COUNT(*) as count FROM `ip_pool` WHERE `status`!='allocated'")
	print(result[0][0])
	return result[0][0]

def executeQuery(db,query):
	#db=getDBConnection()
	cursor=getCursor(db)
	cursor.execute(query)
	result=cursor.fetchall()
	db.commit()
	return result

def runScript():
	pass

def getHypervisorConnection(db,dom0name):
	result=executeQuery(db,"SELECT * FROM `hypervisor` WHERE name='%s' "% (dom0name))
	print(result[0][1],result[0][2],result[0][3])
	try:
		s=pxssh.pxssh()
		s.login(result[0][1],result[0][2],result[0][3])
		return s
	except :
		print ("pxssh failed on login.")
    	


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
	#connection.sendline(command)
	#connection.prompt()





def main(post):
	try:
		db=getDBConnection()
		ip=[] 
		noofslaves=post['number_slave']
		if(count_ip(db)>=noofslaves+1):
			result=executeQuery(db,"SELECT `ip` FROM `ip_pool` WHERE `status`!='allocated'")			
			for i in range(noofslaves+1):
				print(result[i][0])
				ip.append(result[i][0])

			createHadoopCluster(db,post['hypervisor_name'], post['hadoop_name'], post['ram'], noofslaves, ip)
			
			query = "UPDATE `hadoop` SET `status`='created' where hadoop_name='%s'"%post['hadoop_name'];
			executeQuery(db,query)
			
			sql = "INSERT INTO VMdetails (username,VM_name,cpu,ram,storage,hypervisor_name,ip,doe,iscluster) VALUES (%s,%s,%d,%s,%s,%s,%s,%s,%s)" % post['username'],post['VM_name'],post['cpu'],post['ram'],post['storage'],post['hypervisor_name'],ip[0],str(post['doe']),post['iscluster'];
			executeQuery(db,sql)
			
			sql = 
		db.close()
	except:
		db.rollback();


if __name__=="__main__":
	post = {
		"username": "admin",
		"hadoop_name": "trying",
		"description": "testing hadoop cluster",
		"number_slave": 2,
		"cpu": 2,
		"storage": "10GB",
		"ram": "256MB",
		"doe":"25/08/1995",
		"hypervisor_name":"xenserver-trial" 
		}
	main(post)
