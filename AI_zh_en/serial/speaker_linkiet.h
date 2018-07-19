/*
 * file : speaker_linkiet.h
 */

#ifndef  __SPEAKER_LINKITONE_H_
#define  __SPEAKER_LINKITONE_H_

typedef   int		int32;
typedef	  char		int8;
typedef   unsigned int		uint32;


#define   bool		int
#define FALSE  (-1)    
#define TRUE   (0)



#define DEVICE_PORT		"/dev/ttyUSB0"
#define MESSAGE_LINKITONE_PATH_PHONESTATUS		"/home/respeaker/serial/phonestatus.info"
#define MESSAGE_LINKITONE_PATH_RECVMESAGNUM		"/home/respeaker/serial/messagenum.info"
#define MESSAGE_LINKITONE_PATH_LIBSOINFO	"/home/respeaker/serial/libso.info"


typedef struct __usb_serial{

	int32		ser_fd;
	int32		speed;		/* 速率 */
	int32		ctrl;		/* 数据流控制 */
	int32		databits;   /* 数据位   取值为 7 或者8    	*/
	int32		stopbits;	/* 停止位   取值为 1 或者2     	*/
	int32		parity;		/* 效验类型 取值为N,E,O,S */
	int8		port[50];
	int8		precv_phone_message[20];

	int32		(*open)		(void); /* exp : ttyUSB0 */
	void		(*close)	(int32  fd);
	int32		(*serial_config)	(void);
	int32		(*serial_recv)		(int32  fd,uint32 lenth,int8 *buf);
	int32		(*serial_send)		(int32  fd,uint32 lenth,int8 *buf);
	
}USB_SERIAL,*PUSB_SERIAL;

extern bool get_serial(PUSB_SERIAL *ppserial);
extern bool get_pserial(PUSB_SERIAL ppserial);
extern int32 init_devic_def(void);/* 默认初始化 */
extern int32 open_uart_device(void);
extern int32 serial_send(int32  fd,uint32 length,int8 *buf);
extern int32 serial_recv(int32  fd,uint32 length,int8 *buf);
extern int32 serial_config(void);
extern int8 *get_message(void);
extern void test(void);

#endif /* __SPEAKER_LINKITONE_H_ */
