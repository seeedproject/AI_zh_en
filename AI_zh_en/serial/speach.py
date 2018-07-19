##!/usr/bin/python
# coding:utf-8
# import Speech SDK

from evdev import InputDevice,categorize,ecodes
from pypinyin import pinyin, lazy_pinyin
from aip import AipSpeech
from ctypes import *
from pixel_ring import pixel_ring
import mraa

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
 宏开关
'''
TREAD_ON 	= 1
ON			= 0

'''
init AipSpeech object
'''

aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

'''
led ring
'''

def led_pixel_ring():
	en.dir(mraa.DIR_OUT)
	en.write(0)
	pixel_ring.set_brightness(20)
	
	while led_ring :
		try:
				pixel_ring.wakeup()
				time.sleep(0.01)
				pixel_ring.off()
				time.sleep(0.01)
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
		#print(line)
		play_call_audio()
		tmstr = 'open_door'
		line.lower()
		if line[0:7] == tmstr[0:7] :
			play_open_door_audio()
		
		line = f.readline()
	f.close()
	time.sleep(0.001)
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
class baidu_aip_speech(object):
	
	def __init__(self,_path,_format):
		self.path 	= _path
		self.format = _format
		'''	
		read file 
		'''
	def get_file_content(self):
		with open(self.path, 'rb') as fp:
			return fp.read()
		'''
		recognition local file
		'''
	def parse_speech(self):
		data = aipSpeech.asr(baidu_aip_speech.get_file_content(self), self.format, 16000, {
			'dev_pid': '1536',
		})
		print(data)
		
		string = json.loads(json.dumps(data))
		
		if string['err_no'] == 0:
			pstr = str(string['result'])
			str_doc = pstr.replace("u\'","").replace("\'","").replace("[","").replace("]","").decode('unicode_escape').replace("]","").strip()
			#parse_ch = str(lazy_pinyin(str_doc)).replace("u\'","").replace("[","").replace("]","").replace("\'","").decode('unicode_escape')
			parse_ch = str(lazy_pinyin(str_doc)).decode('unicode_escape').replace("u","").replace("[","").replace("]","").strip()
			#print(str_doc)
			parse_name = ''.join(eval(parse_ch))
			#print(parse_name)
			ret_phonenumber = search_user(parse_name)
			
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
录音时间长度为5s (-d 2)
'''
def record_hander():
	global is_record
	os.system("arecord -d 2 -r 16000 -f S16_LE -t wav /home/respeaker/serial/test.wav")
	is_record = True

	
'''
 call 调用
'''
def pre_play(v):
    global is_pressed,is_music,is_record,is_noteinfo,led_ring
	
	
    while True:
        if is_pressed  == True:
		
			'''
			("欢迎光临柴火创客空间，请问有什么可以帮到您？")
			'''
			os.system("mpg123 /home/respeaker/serial/welcome.mp3") 
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
					
					par = baidu_aip_speech('/home/respeaker/serial/test.wav', 'wav')
					
					if par.parse_speech() == 0 :
					
						is_music	= False
						
					else:
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
	time.sleep(0.001)
	
	
		
'''
访客按键处理
'''		
def key_hander(v):
	global is_pressed,is_noteinfo,led_ring
	
	key = InputDevice("/dev/input/event0")
	for event in key.read_loop():
		if event.type == ecodes.EV_KEY:
			print(categorize(event)) 
			led_ring 	= True
			is_pressed 	= True
			is_noteinfo = True
			
			
'''
 数据解析及电话连线时提示音
'''
def play_music(v):
	global is_music
	
	while True:
		led_pixel_ring()
		
		if is_music == True:
			os.system("mpg123 /home/respeaker/serial/tishi.mp3")
			
		
		time.sleep(1)
		
def play_call_audio():
		global is_callflags
		
		if is_callflags == True :
			is_callflags = False
			os.system("mpg123 /home/respeaker/serial/callinfo.mp3")
			
def play_call_error_audio():
			os.system("mpg123 /home/respeaker/serial/errorinfo.mp3")
			
def play_open_door_audio():
			os.system("mpg123 /home/respeaker/serial/open_info.mp3")
			
def play_respeach():
			os.system("mpg123 /home/respeaker/serial/re_speach.mp3")
			

'''
recv linkitone ask
'''	
def recv_message(v):
	global led_ring
	while True:
		
		len = c_serial.serial_recv(gfd,30,objSerial.precv_phone_message)
		#print(len)
		
		if len > 0 :
			led_ring 	= True
			#fileHandle = open ( '/home/respeaker/serial/test.txt', 'ab+' )
			#fileHandle.write(str(len))
			#fileHandle.close()
			read_ask()
			read_askmessage()	
			led_ring 	= False
	time.sleep(0.001)
	
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
		
		'''
		调试时CTRL + C 处理
		'''
		signal.signal(signal.SIGINT, CtrlC)
		signal.signal(signal.SIGTERM, CtrlC)

		thread_key  = threading.Thread(target=key_hander,args=(1,))
		thread_play = threading.Thread(target=pre_play, args=(1,))
		thread_music = threading.Thread(target=play_music, args=(1,))
		thread_recv = threading.Thread(target=recv_message, args=(1,))
		
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
				pass
			
		'''
		异常处理
		'''	
	except Exception,exc:
		print exc
	
	
