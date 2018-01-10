# package Configuration

import configparser

def getConfig():
	config = configparser.ConfigParser()
	config.read('cloud_middleware.ini')
	return config

def get_proxy_port():
	config = getConfig()
	return config.getint('http-proxy-details','port')

def get_proxy_host():
	config = getConfig()
	return config.get('http-proxy-details','host')

def get_proxy_username():
	config = getConfig()
	return config.get('http-proxy-details','username')

def get_proxy_password():
	config = getConfig()
	return config.get('http-proxy-details','password')

def get_mail_host():
	config = getConfig()
	return config.get('email-login-details','host')

def get_mail_port():
	config = getConfig()
	return config.getint('email-login-details','port')

def get_mail_password():
	config = getConfig()
	return config.get('email-login-details','password')

def get_mail_username():
	config = getConfig()
	return config.get('email-login-details','username')

def get_db_host():
	config = getConfig()
	return config.get('database-connection-settings','host')

def get_db_username():
	config = getConfig()
	return config.get('database-connection-settings','username')

def get_db_password():
	config = getConfig()
	return config.get('database-connection-settings','password')

def get_db_name():
	config = getConfig()
	return config.get('database-connection-settings','db-name')

if __name__=="__main__":
	print(get_db_name())