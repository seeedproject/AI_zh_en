/*
 * file : speaker_linkiet.c
 *
 * communication protocol :
 *
 * respeaker				linkitone
 * com:						com:ASK
 * phone		--------->   
 * recv			<--------	ok/oop
 * phone numb   --------->  
 * recv			<---------	ok/oop
 *
 *
 * 
 * bulid	c lib
 * gcc -shared -Wl,-soname,adder -o speaker_linkiet.so -fPIC speaker_linkiet.c
 *
 * call c lib
 * from ctypes import *
 * adder = CDLL('path/XXXX.so') ; path = ./speaker_linkiet.so or /hoem/speaker_linkiet.so
 *
 */
 
#include <stdio.h>   
#include <errno.h>  
#include <sys/stat.h>
#include <fcntl.h>  
#include <termios.h>    
#include <stdlib.h> 
#include <sys/types.h>
#include <unistd.h> 
#include <string.h>
#include <sys/ioctl.h>
#include <syslog.h>

#include "speaker_linkiet.h"


static USB_SERIAL   g_sriral;
#define ASSERT_RTN(p,rtn)    {!(p)?printf("Assert failed: file \"%s\", line %d\n", __FILE__, __LINE__): p;if(!(p)) {return rtn;} }

bool get_serial(PUSB_SERIAL *ppserial)
{

	ASSERT_RTN(ppserial!=NULL,FALSE);
	*ppserial = &g_sriral;

	 return TRUE;
}

bool get_pserial(PUSB_SERIAL pserial)
{
	PUSB_SERIAL ppserial;
	
	//ASSERT_RTN(ppserial!=NULL,FALSE);
	pserial =  &g_sriral;

	 return TRUE;
}


/*
 *  open serial
 *	retrun
 *  error		:  < 0
 *  successful	:  fd
 */
static int32 open_uart(void)
{
	PUSB_SERIAL pserial;

	printf("open start !\n");
	get_serial(&pserial);

	if(!pserial)
		printf("malloc error!\n");
	
	pserial->ser_fd = open("/dev/ttyUSB0",O_RDWR|O_NONBLOCK);
	if( pserial->ser_fd < 0){
		perror("open serial failed!");
		return FALSE;
	}


	if(fcntl(pserial->ser_fd,F_SETFL,0) < 0){
		printf("fcntl failed!\n");
		return FALSE;
	}
	

	if(0 == isatty(STDIN_FILENO)){
		printf("standard input is not a terminal device\n");
		return FALSE;
	}
	
	return  pserial->ser_fd;

	printf("open successfull !\n");
}

/*close serial */
static void close_uart(int32 fd)
{
	close(fd);
}


int32 serial_config(void)
{

	
	
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}
	

#if 1
	struct termios tio;

	memset(&tio,0,sizeof(tio));
	tio.c_iflag=0;
	tio.c_oflag=0;
	tio.c_cflag=CS8|CREAD|CLOCAL;           // 8n1, see termios.h for more information
	tio.c_lflag=0;
	tio.c_cc[VMIN]=1;
	tio.c_cc[VTIME]=1;

	cfsetospeed(&tio,B115200);            // 115200 baud
	cfsetispeed(&tio,B115200);            // 115200 baud

	tcsetattr(pserial->ser_fd,TCSANOW,&tio);
#else
	
	struct termios	opt;

	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}

	memset(&opt,0,sizeof(opt));
	

	// 输入输出速率设置 

	
	switch(pserial->speed)
	{
		case 2400:
			cfsetispeed(&opt,B2400);
			cfsetospeed(&opt,B2400);
		break;
		case 4800:
			cfsetispeed(&opt,B4800);
			cfsetospeed(&opt,B4800);
		break;
		case 9600:
			cfsetispeed(&opt,B9600);
			cfsetospeed(&opt,B9600);
		break;
		case 115200:
			cfsetispeed(&opt,B115200);
			cfsetospeed(&opt,B115200);
		break;
		case 460800:
			cfsetispeed(&opt,B460800);
			cfsetospeed(&opt,B460800);
		break;
		default:
			cfsetispeed(&opt,B9600);
			cfsetospeed(&opt,B9600);
		break;
	}
	
	printf("speed :%d \n",pserial->speed);
	
	
	

	//设置数据流控制 
	
    switch(pserial->ctrl)    
    {    
          
        case 0 ://不使用流控制    
              opt.c_cflag &= ~CRTSCTS;    
              break;       
          
        case 1 ://使用硬件流控制    
              opt.c_cflag |= CRTSCTS;    
              break;    
        case 2 ://使用软件流控制    
              opt.c_cflag |= IXON | IXOFF | IXANY;    
              break;    
    }    
//printf("ctrl :%d \n",pserial->ctrl);

	//设置数据位    
    //屏蔽其他标志位       
	switch (pserial->databits)    
	{      
		case 5    :    
			opt.c_cflag |= CS5;    
		break;    
		case 6    :    
			opt.c_cflag |= CS6;    
		break;    
		case 7    :        
			opt.c_cflag |= CS7;    
		break;    
		case 8:        
			opt.c_cflag |= CS8;    
		break;      
		default:       
			fprintf(stderr,"Unsupported data size\n");   
		
		return FALSE;     
	}  
	//printf("databits :%d \n",pserial->databits);
    //设置校验位    
	switch (pserial->parity)    
	{      
		case 'n':    
		case 'N': //无奇偶校验位。    
			opt.c_cflag &= ~PARENB;     
			//opt.c_iflag &= ~INPCK;        
		break;     
		case 'o':      
		case 'O'://设置为奇校验        
			opt.c_cflag |= (PARODD | PARENB);     
			opt.c_iflag |= INPCK;                 
		break;     
		case 'e':     
		case 'E'://设置为偶校验      
			opt.c_cflag |= PARENB;           
			opt.c_cflag &= ~PARODD;           
			opt.c_iflag |= INPCK;          
		break;    
		case 's':    
		case 'S': //设置为空格     
			opt.c_cflag &= ~PARENB;    
			opt.c_cflag &= ~CSTOPB;    
		break;     
		default:      
			fprintf(stderr,"Unsupported parity\n"); 
			
		return FALSE;     
	}    
	//printf("parity :%d \n",pserial->parity);
	// 设置停止位     
	switch (pserial->stopbits)    
	{      
		case 1:       
			opt.c_cflag &= ~CSTOPB; break;     
		case 2:       
			opt.c_cflag |= CSTOPB; break;    
		default:       
			fprintf(stderr,"Unsupported stop bits\n");  
		
		return FALSE;    
	}    

	//printf("stopbits :%d \n",pserial->stopbits);
	
	//设置等待时间和最小接收字符    
	opt.c_cc[VTIME] = 1; /* 读取一个字符等待1*(1/10)s */      
	opt.c_cc[VMIN] = 0; /* 读取字符的最少个数为1 */    

	//如果发生数据溢出，接收数据，但是不再读取 刷新收到的数据但是不读    
	tcflush(pserial->ser_fd,TCIFLUSH);    
       
	//激活配置 (将修改后的termios数据设置到串口中）    
	if (tcsetattr(pserial->ser_fd,TCSANOW,&opt) != 0)      
	{    
		perror("com set error!\n");

		return FALSE;     
	}  
#endif

	return TRUE;     
	
}
int open_message(int8 *path,int8 *ask)
{
	int32 fd;
	
	openlog("clibinfo", LOG_PID|LOG_CONS, LOG_USER);  
	//printf("**********************************\n");
	//printf("recvask 00: %s  %s \n",ask,path);
	fd = open(path,O_RDWR|O_CREAT);
	
	syslog(LOG_INFO, "%s", path); 
	
	if(fd < 0){
		perror("open error");
		return -1;
	}
	
	syslog(LOG_INFO, "%s", ask);
	//printf("recvask: %s  %s \n",ask,path);
	//printf("********************2**************\n");
	
	write(fd,ask,strlen(ask));
	
	return fd;
}

bool write_file(int8 *ask)
{
	
	int32 fd;
	if(!ask)
		return FALSE;
	
	if(strncmp("phoneNumber:",ask,12) == 0 ){
		//printf("recv message number %s \n",ask); 
		fd = open_message(MESSAGE_LINKITONE_PATH_RECVMESAGNUM,ask);/*recv message number*/
		close(fd);
		
	}else{
		//printf("phone status %s \n",ask); 
		fd = open_message(MESSAGE_LINKITONE_PATH_PHONESTATUS,ask);/*phone status*/
		close(fd);
		
	}
	
	
	
	
	return TRUE;
	
}


int32 serial_recv(int32  fd,uint32 length,int8 *buf)
{

	int32 len,fs_sel;    
	fd_set fs_read;    
	int8 rv_buf[20] = {0};
	struct timeval time;   
	static  int8 save_masseg[40] = {0};
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}

	FD_ZERO(&fs_read);    
	FD_SET(pserial->ser_fd,&fs_read);    

	time.tv_sec = 0;    
	time.tv_usec = 10;    

	//使用select实现串口的多路通信    
	fs_sel = select(pserial->ser_fd+1,&fs_read,NULL,NULL,&time);
	if(fs_sel){    
		len = read(pserial->ser_fd,rv_buf,length); 
		if(len > 0)	{	
			//printf("I am right!(version1.2) len = %d fs_sel = %d  %s \n",len,fs_sel,rv_buf); 
			memset(pserial->precv_phone_message,0,20);
			
			snprintf(pserial->precv_phone_message,len,rv_buf);
			
			
			if(strncmp("CLEAER",pserial->precv_phone_message,5) == 0 || strncmp("NOSMS",pserial->precv_phone_message,5) == 0){
				write_file("NULL");
				return len; 
			}
			if(strncmp("open_door",pserial->precv_phone_message,9) == 0){
				write_file(pserial->precv_phone_message);
				memset(save_masseg,0,40);
				return len;
			}
			
			if(strncmp(save_masseg,pserial->precv_phone_message,strlen(pserial->precv_phone_message)) != 0){
				write_file(pserial->precv_phone_message);
				memset(save_masseg,0,40);
				snprintf(save_masseg,len,rv_buf);
			}
			return len;   
		}		
	}   
	
		
	return FALSE;    
           
}

void test(void)
{
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return ;
	}
	printf("recv:%s\n",pserial->precv_phone_message); 
}

int8 *get_message(void)
{
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return NULL;
	}
	//printf("recv222:%s\n",pserial->precv_phone_message); 
	return pserial->precv_phone_message;
	
}

int32 serial_send(int32  fd,uint32 length,int8 *buf)
{
	int32 len = 0;    
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}
	
	len = write(pserial->ser_fd,buf,length);  
//printf("send data 2is %s\n",buf);  	
	if (len == length ) {    
		printf("send data is %s\n",buf);  
		return len;    
	}         
	       
	tcflush(pserial->ser_fd,TCOFLUSH);
	
	return FALSE;       
}


/* 默认初始化 */
int32 init_devic_def(void)
{
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}

	pserial->speed			= 115200;
	pserial->ctrl			= 0;
	pserial->databits 		= 8;
	pserial->parity			= 'N';
	pserial->stopbits		= 1;
	sprintf(pserial->port,"%s",DEVICE_PORT);
	pserial->ser_fd			= -1;

	
	pserial->open			=	open_uart;
	pserial->close			=	close_uart;
	pserial->serial_config	=   serial_config;
	//pserial->serial_recv	=	serial_recv;
	pserial->serial_send	=	serial_send;

	printf("#### init ok!\n");
	
	return TRUE;
}

int32 open_uart_device(void)
{
	int32 fd,err;  
	 
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}

	fd = pserial->open(); //打开串口，返回文件描述符  
     
    
    pserial->serial_config();    
        
    

	return fd;
	
}

/*serial test*/
#if 0

int32 main(int32 argc, char **argv)    
{    
    int32 fd;                            //文件描述符    
    int32 err;                           //返回调用函数的状态    
    int32 len;                            
    int32 i;    
    char rcv_buf[100];              
    char send_buf[20]="test";  
    if(argc != 2)    
    {    
        printf("Usage: %s  (receive data) \n",argv[0]);    
        return FALSE;    
    }    

	init_devic_def();
	
	PUSB_SERIAL pserial;
		
	get_serial(&pserial);

	if(!pserial){
		printf("malloc error!\n");
		return FALSE;
	}

	
	
	 
    fd = pserial->open(); //打开串口，返回文件描述符  
     
    do  
    {    
        err = pserial->serial_config();    
        
    }while(FALSE == err || FALSE == fd);    
/*       
    if(0 == strcmp(argv[1],"0"))    
    {    
        for(i = 0;i < 10;i++)    
        {    
            len = pserial->serial_send(fd,10,send_buf);    
            if(len > 0)    
                printf(" %d time send %d data successful\n",i,len);    
            else    
                printf("send data failed!\n");    
                              
            sleep(2);    
        }    
        pserial->close(fd);                 
    }    
    else    */
    {                                          
        while (1) //循环读取数据    
        {    

	

#if 1
			
            len = pserial->serial_recv(fd,99, rcv_buf);    
            if(len > 0)    
            {    
                rcv_buf[len] = '\0';    
                printf("receive data is %s\n",rcv_buf);    
                printf("len = %d\n",len);  
				len = pserial->serial_send(fd,10,rcv_buf);  
            }    
            else    
            {    
                printf("cannot receive data\n");    
				len = pserial->serial_send(fd,10,rcv_buf);    
	            if(len > 0)    
	                printf(" %d time send %d data successful\n",i,len);    
	            else    
	                printf("send data failed!\n"); 
	            }    
            usleep(500000);   
#endif
        }                
        pserial->close(fd);       
    }    
}    

#endif




