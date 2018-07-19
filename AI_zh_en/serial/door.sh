#!bin/bash
lock="speach.py"

start(){  
        echo "service start...."  
 #       su root -c "python /root/python/py_stock/src/crawler/py_stock.py &" 
		/home/respeaker/serial/speach.py 
}  

stop(){
	echo "service stop...."
	pkill -f $lock
} 

status(){  
        if [ -e $lock ];then  
            echo "$0 service start"  
        else  
            echo "$0 service stop"  
        fi  
}  

restart(){  
        stop  
        start  
}  
case "$1" in  
"start")  
        start  
        ;;  
"stop")  
        stop  
        ;;  
"status")  
        status  
        ;;  
"restart")  
        restart  
        ;;  
*)  
        echo "$0 start|stop|status|restart"  
        ;;  
esac  