##!/usr/bin/python
# coding:utf-8
# import Speech SDK

'''
	文件名 : speach.py
	支持百度中英语音，中文识别率较高，但英语识别率不理想，
	若想用中文请打开宏开关 ，中英文切换，true = zh , false = en
	同时改变百度为云端解析
	bing /baidu 宏开关 False=baidu ,True=bing
	
'''

from evdev import InputDevice,categorize,ecodes
from pypinyin import pinyin, lazy_pinyin
from aip import AipSpeech
from ctypes import *
from pixel_ring import pixel_ring
from respeaker.bing_speech_api import BingSpeechAPI

import mraa
import logging
import ConfigParser
import serial.tools.list_ports
import threading,signal
import time
import sys
import os
import re
import json


is_pressed  	= False
is_record		= False
is_music		= False
is_noteinfo 	= False
is_callflags 	= False
flags 			= 0
gfd				= -1
led_ring		= False
parse_flags 	= False
key_time_zh		= 2
key_time_en		= 4
starttime 		= 0
lasttime  		= 0

'''
bing key
'''
BING_KEY = 'b0ccafde97ed4d888ef5f4ef95d93214'

'''
中英文切换，true = zh , false = en
'''
#zh_en_on        = False
zh_en_on        = True

'''
 宏开关
'''
TREAD_ON 	= 1
ON			= 0

'''
bing /baidu 宏开关 False=baidu ,True=bing
'''
#BING_BAIDU_ON = True
BING_BAIDU_ON = False

'''
led
'''
en = mraa.Gpio(12)

'''
 C lib call
'''
c_serial = CDLL('/home/respeaker/serial/speaker_linkiet.so')

def c_uartlib():
	c_serial.init_devic_def()
	gfd = c_serial.open_uart_device()
	c_serial.serial_config()



class USB_SERIAL(Structure):
	_fields_= [('precv_phone_message',c_char*20),]
	
objSerial = USB_SERIAL()	




'''
c_serial.get_pserial.argtypes = [POINTER(USB_SERIAL)]

c_serial.get_pserial(byref(objSerial))

#c_serial.get_message.argtypes = [POINTER(USB_SERIAL)]
'''

'''
bing  api
'''
def bing_api_call():
	logging.basicConfig(level=logging.DEBUG)

class remesaage:
	def __init__(self):
		self.message = ''
		
reobjectmessage = remesaage()
reobjectmessage.reobjectmessage = 'not change'

print(reobjectmessage.reobjectmessage)

'''
defined
'''

APP_ID = '11203359'
API_KEY = 'wG9Iqfg2OplwQmXQaM5fxzRY'
SECRET_KEY = '2VuEDoSSi7rgFUggYSfzrTeQ4YGLhSlW'



'''
init AipSpeech object
'''

aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

'''
led ring
'''
en.dir(mraa.DIR_OUT)

def led_pixel_ring():
	en.write(0)
	pixel_ring.set_brightness(20)
	
	
	while led_ring :
		try:
			pixel_ring.wakeup()
			time.sleep(0.1)
			pixel_ring.off()
			time.sleep(0.1)
			pixel_ring.off()
		except KeyboardInterrupt:
			break

	pixel_ring.off()
	en.write(1)
	
'''
蓝牙通信
'''
'''
def  seria_common() :
	plist = list(serial.tools.list_ports.comports())

	if len(plist) <= 0:
		print "The Serial port can't find!"
	else:
		plist_0 =list(plist[0])
		serialName = plist_0[0]
		serialFd = serial.Serial(serialName,9600,timeout = 60)
		print "check which port was really used >",serialFd.name
'''
'''
 list
'''
def convert_to_list():
	result=[]
	fd = file("/home/respeaker/serial/collection.txt", "r")
	
	for line in fd.readlines():
		result.append(list(line.lower().split(',')))
	
	#print(result)
	'''
	for item in result:
		for it in item :
			print(it)
	'''
	fd.close()
	
	return result
	
def fuzzyfinder(parse_name,result):
	suggestions = []
	pattern = '.*'.join(parse_name) 		# Converts 'tes' to 't.*e.*s'
	regex = re.compile(pattern)     		# Compiles a regex.
	for item in result:
		for it in item:
			match = regex.search(it)  		# Checks if the current item matches the regex.
			if match:
				suggestions.append(it)
		
		
	print(suggestions)
	return suggestions
	
'''
 parse local file
'''
def search_user(user):
	#print(len(user))
	print(user[0:len(user)-3])
	cf = ConfigParser.ConfigParser()
	cf.read("/home/respeaker/serial/username.txt")
	is_ = cf.has_option("db", user[0:len(user)-3])
	if is_ :
		db_phone = cf.get("db", user[0:len(user)-3])
		if db_phone.isdigit() :
			return db_phone
		else:
			return 0;
	else:
		return 0;	
		
'''
 parse local file
'''
def search_user_en(user):
	print(len(user))
	print(user)
	cf = ConfigParser.ConfigParser()
	cf.read("/home/respeaker/serial/username_en.txt")
	is_ = cf.has_option("db", user)
	if is_ :
		db_phone = cf.get("db", user)
		if db_phone.isdigit() :
			return db_phone
		else:
			return 0;
	else:
		return 0;

def search_allphnoe(number):
	fd = open("/home/respeaker/serial/phone_link.txt")
	line = fd.readline()
	while line:
		
		print(line[0:12])
		
		tmp = number[12:23]
		print(tmp)
		
		if line[0:11] == tmp :
			#print("find ok")
			c_serial.serial_send(gfd,6,"recvok");
				
			fd.close()
			return 0
		line = fd.readline()
	fd.close()
	
	return -1
	
	
'''
read linkitone ask
'''	
def read_ask():
	f = -1
	try:
		f = open("/home/respeaker/serial/phonestatus.info")
	except Exception,e:
		f = open("/home/respeaker/serial/phonestatus.info","wb+")
		f.close()
		return 0
		
	line = f.readline()
	
	#print("recv phone status:")
	while line:
		print(line)
		play_call_audio()
		tmstr = 'open_door'
		line.lower()
		if line[0:7] == tmstr[0:7] :
			play_open_door_audio()
		
		line = f.readline()
	f.close()
	time.sleep(0.1)
	cf = open("/home/respeaker/serial/phonestatus.info","wb+")
	cf.close()
	#print("recv phone end:")
	
def read_askmessage():
	fd = -1
	#fileHandle = open ( '/home/respeaker/serial/test.txt', 'ab+' )
	#fileHandle.write("recv start")
	#fileHandle.close()
	try:
		fd = open("/home/respeaker/serial/messagenum.info")
		
	except Exception,e:
			fd = open("/home/respeaker/serial/messagenum.info","wb+")
			fd.close()
			return 0
	#print("read Message:")	
	#fileHandle = open ( '/home/respeaker/serial/test.txt', 'ab+' )
	#fileHandle.write("recv info")
	#fileHandle.close()
	line = fd.readline()
	#fileHandle = open ( '/home/respeaker/serial/test.txt', 'ab+' )
	#fileHandle.write(line)
	#fileHandle.close()
	
	#fileHandle = open ( '/home/respeaker/serial/test.txt', 'ab+' )
	#fileHandle.write(" end ")
	#fileHandle.close()
	while line:
		#print(line)
		num = search_allphnoe(line)
		if num == 0:
			#fd.truncate()
			fd.close()
			fd = open("/home/respeaker/serial/messagenum.info","wb+")
			fd.close()
			return 0
		line = fd.readline()
	#fd.truncate()
	fd.close()
	return -1
	
'''
 百度API云端处理
'''
class baidu_bing_aip_speech(object):
	
	def __init__(self,_path,_format):
		self.path 	= _path
		self.format = _format
		'''	
		read file 
		'''
	def get_file_content(self):
		with open(self.path, 'rb') as fp:
			return fp.read()
			
	def bing__parse_speech(self):
		bing = BingSpeechAPI(key=BING_KEY)
		try:                      
			fd = open(self.path)
			conect = fd.read(-1)
			text = bing.recognize(conect)
			fd.close()
			if text:           
				print('Recognized %s' % text)
				#f = open("out.txt", "w") 
				#print >> f, "%s " % (text)
				#f.close()
				#print(strlen)
				#print(str_doc[0:strlen])
				convert_lis = convert_to_list()
				#print("******12*********")
				find_name = fuzzyfinder(text,convert_lis)
				#print("***************")
				#print(find_name)
				#print("******1*********")
				ret_phonenumber = search_user_en(''.join(find_name).lower())
				#print("************************")
				#print(ret_phonenumber)
				if ret_phonenumber:
					global is_callflags
					is_callflags = True
					c_serial.serial_send(gfd,11,ret_phonenumber);
					print("************************")
				else:
					play_call_error_audio()
					
				return 0
				
			else:
				print('Recognized error %s' % text)
				return -1
				
		except Exception as e:               
			print(e.message)  
		
		'''
		recognition local file
		'''
	def baidu_parse_speech(self):
		data = ""
		if zh_en_on :
			'''
			zh
			'''
			data = aipSpeech.asr(baidu_bing_aip_speech.get_file_content(self), self.format, 16000, {
				'dev_pid': '1536',
			})
		else:
			'''
			en
			'''
			data = aipSpeech.asr(baidu_bing_aip_speech.get_file_content(self), self.format, 16000, {
				'dev_pid': '1737',
			})
			
		print(data)
		
		string = json.loads(json.dumps(data))
		
		if string['err_no'] == 0:
			ret_phonenumber = ""
			pstr = str(string['result'])
			str_doc = pstr.replace("u\'","").replace("\'","").replace("[","").replace("]","").decode('unicode_escape').replace("]","").strip()
						
			if zh_en_on:
				'''
				zh
				'''
				parse_ch = str(lazy_pinyin(str_doc)).decode('unicode_escape').replace("u","").replace("[","").replace("]","").strip()
				#print(str_doc)
				parse_name = ''.join(eval(parse_ch))
				#print(parse_name)
				ret_phonenumber = search_user(parse_name)
			else:
				'''
				en
				'''
				
				print(str_doc)
				#parse_ch = str_doc.strip()
				#print(parse_ch)
				strlen = (len(str_doc) - 1)
				
				#print(strlen)
				#print(str_doc[0:strlen])
				convert_lis = convert_to_list()
				#print("******12*********")
				find_name = fuzzyfinder(str_doc[0:strlen],convert_lis)
				#print("***************")
				#print(find_name)
				#print("******1*********")
				ret_phonenumber = search_user_en(''.join(find_name).lower())
				#print("************************")
			#print(ret_phonenumber)
			if ret_phonenumber:
				global is_callflags
				is_callflags = True
				c_serial.serial_send(gfd,11,ret_phonenumber);
			else:
				play_call_error_audio()
			
			return 0
		else :
			
			return -1
			
			
		
'''
录音时间长度为5s (-d 3)
'''
def record_hander():
	global is_record
	os.system("arecord -d 3 -r 16000 -f S16_LE -t wav /home/respeaker/serial/test.wav")
	is_record = True

	
'''
 call 调用
'''
def pre_play(v):
    global is_pressed,is_music,is_record,is_noteinfo,led_ring,parse_flags
	
	
    while True:
        if is_pressed  == True:
		
			if parse_flags ==  False:
				'''
				("欢迎光临柴火创客空间，请问有什么可以帮到您？")
				'''
				if zh_en_on :
					os.system("mpg123 /home/respeaker/serial/welcome.mp3") 
				else:
					os.system("mpg123 /home/respeaker/serial/welcome_en.mp3") 
			
				
			is_pressed	= False
			
			'''
			 录音开始
			'''
			record_hander()
			#global is_record
			'''
			 录音完成
			'''
			
			
			
			try:
				if is_record == True :
					is_record = False
					'''
					数据解析及电话连线使能
					'''
					#global is_music
					
					is_music	= True
					
					par = baidu_bing_aip_speech('/home/respeaker/serial/test.wav', 'wav')
					
					'''
					baidu api call
					'''
					if BING_BAIDU_ON == False:
						if par.baidu_parse_speech() == 0 :
							is_music	= False
							parse_flags = False
						else:
							parse_flags = True
					else:
						if par.bing__parse_speech() == 0 :
							is_music	= False	
							parse_flags = False
						else:
							parse_flags = True
							
					if parse_flags :
						'''
						解析错误时，重复一次联系人提示音
						'''
						is_music 	= False	
						
						time.sleep(1)
						
						if is_noteinfo == True :
							led_ring 	= True
							play_respeach()
							is_pressed  = True
							is_noteinfo = False
			
			except Exception,e:
				is_music 	= False
				is_noteinfo = False
				print e.message
			led_ring 	= False
	time.sleep(0.1)

'''
长按2S,切换为中文，长按4S切换为英语
'''	
def zh_en_change(time):
	
	global key_time_zh,key_time_en,zh_en_on,BING_BAIDU_ON
	
	if key_time_zh == time:
		zh_en_on        = True
		BING_BAIDU_ON   = False
		print("Change zh\n")
	elif key_time_en == time :
		zh_en_on        = False
		BING_BAIDU_ON 	= True
		print("Change en\n")
'''
访客按键处理
'''		
def key_hander(v):
	global is_pressed,is_noteinfo,led_ring,starttime,lasttime

	
	key = InputDevice("/dev/input/event0")
	for event in key.read_loop():
		
		if event.type == ecodes.EV_KEY:
			print(categorize(event)) 
			
			
			'''
			hold time
			'''
			if event.value == 2 :
				lasttime = event.sec
				sp_time = lasttime - starttime 
				print(sp_time)
				
				if sp_time >= key_time_zh and sp_time <= key_time_en:
					zh_en_change(sp_time)
				
				'''
				down
				'''
			elif event.value == 1 :
				starttime = event.sec
				'''
				up
				'''
			else:
				led_ring 	= True
				is_pressed 	= True
				is_noteinfo = True
				starttime = 0
				lasttime  = 0
				
		
			
'''
 数据解析及电话连线时提示音
'''
def play_music(v):
	global is_music
	
	while True:
		
		if is_music == True:
			os.system("mpg123 /home/respeaker/serial/tishi.mp3")
			
		
		time.sleep(1)
		
def play_call_audio():
		global is_callflags
		
		if is_callflags == True :
			is_callflags = False
			if zh_en_on :
				'''
				正在为您接通，请等待...
				'''
				os.system("mpg123 /home/respeaker/serial/callinfo.mp3")
			else:
				os.system("mpg123 /home/respeaker/serial/callinfo_en.mp3")
			
def play_call_error_audio():
			if zh_en_on :
				'''
				抱歉，我已经很努力的去为您寻找要找的人，可是仍然没能找到
				'''
				os.system("mpg123 /home/respeaker/serial/errorinfo.mp3")
			else:
				os.system("mpg123 /home/respeaker/serial/errorinfo_en.mp3")
			
def play_open_door_audio():
			#global led_ring
			if zh_en_on :
				'''
				您好，请进，门已为您打开，欢迎来到柴火创客空间
				'''
				os.system("mpg123 /home/respeaker/serial/open_info.mp3")
			else:
				os.system("mpg123 /home/respeaker/serial/open_info_en.mp3")
				
			#led_ring 	= False
			#pixel_ring.off()
			#en.write(1)
			
def play_respeach():
			if zh_en_on :
				'''
				我没能听能听清楚，请再说一遍
				'''
				os.system("mpg123 /home/respeaker/serial/re_speach.mp3")
			else:
				os.system("mpg123 /home/respeaker/serial/re_speach_en.mp3")
			

'''
recv linkitone ask
'''	
def recv_message(v):
	global led_ring
	while True:
		
		len = c_serial.serial_recv(gfd,30,objSerial.precv_phone_message)
		print(len)
		
		if len > 0 :
			led_ring 	= True
			#fileHandle = open ( '/home/respeaker/serial/test.txt', 'ab+' )
			#fileHandle.write(str(len))
			#fileHandle.close()
			read_ask()
			read_askmessage()	
			led_ring 	= False
			
	time.sleep(0.1)


		
	
	
	
'''
 CTRL + C
'''
def CtrlC(signum, frame):
	os.kill(os.getpid(),signal.SIGKILL)

	
'''
 main  start ...
'''
if __name__ == "__main__":
	'''
	if os.geteuid():
		args = [sys.executable] + sys.argv
		os.execlp('sudo','sudo',*args)
		#os.execlp('su', 'su', '-c', ' '.join(args))
	'''
	try:
		c_uartlib()
		bing_api_call()
		
		'''
		调试时CTRL + C 处理
		'''
		signal.signal(signal.SIGINT, CtrlC)
		signal.signal(signal.SIGTERM, CtrlC)

		thread_key  	= threading.Thread(target=key_hander,args=(1,))
		thread_play 	= threading.Thread(target=pre_play, args=(1,))
		thread_music 	= threading.Thread(target=play_music, args=(1,))
		thread_recv 	= threading.Thread(target=recv_message, args=(1,))
		
		
		thread_key.setDaemon(True)
		thread_play.setDaemon(True)
		thread_music.setDaemon(True)
		thread_recv.setDaemon(True)
	
		thread_key.start()
		thread_play.start()
		thread_music.start()
		thread_recv.start()
			
		
		if TREAD_ON == ON :
			thread_key.join()
			thread_play.join()
			thread_music.join()
			thread_recv.join()
			
		else :
			while True:
				led_pixel_ring()
				time.sleep(1)
				pass
			
		'''
		异常处理
		'''	
	except Exception,exc:
		print exc
	
	
