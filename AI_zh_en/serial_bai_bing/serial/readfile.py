import sys
import json
import ConfigParser
import os


cf = ConfigParser.ConfigParser()
cf.read("./username.txt")
secs = cf.sections()
print 'sections:', secs, type(secs)
opts = cf.options("db")
print 'options:', opts, type(opts)
kvs = cf.items("db")
print 'db:', kvs
db_host = cf.has_option("db", "jianghong")
if db_host :
	db_host = cf.get("db", "jianghong",raw=True)
	print(db_host)
	if db_host.isdigit():
		print "db_host:", db_host

'''
with open("./username.txt") as file:
	for line in file:
		#search = line.find('{')
		#print(search)
		s_strip = line.strip()
		print(s_strip.find('{'))
		
		print(s_strip)
		if s_strip :
			d = {key:value for key,value in json.loads(s_strip).items()}
			print(d)
		
		
'''
'''
pf = open("./username.txt","r")
line = pf.readline()
while line:
	
	if line.find(u"#")  !=-1 :
		print(line)
	else:
		if line != 'n' :
			
			print(line)
			key_value = dict(line)
			print(key_value)
			#for key  in rows:
			#	print 'key is %d,value is %s'%(rows,rows[key])

			
#		if 'jianghong' == string['jianghong'] :
#			print(arr)
#		else:
#			prin("not thing")
		
	line = pf.readline()
pf.close()
'''