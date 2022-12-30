import socket
import os
import sys
import struct
import cv2
 
 
def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #IP地址留空默认是本机IP地址
        s.bind(('', 8088))
        s.listen(7)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
 
    print("连接开启，等待传图...")
	
    while True:
        sock, addr = s.accept()
        deal_data(sock, addr)
 
    s.close()
 
 
def deal_data(sock, addr):
    print("成功连接上 {0}".format(addr))
 
    while True:
        fileinfo_size = struct.calcsize('128sl')
        buf = sock.recv(fileinfo_size)
        if buf:
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.decode().strip('\x00')
            #PC端图片保存路径
            new_filename = os.path.join('./', fn)
 
            recvd_size = 0
            fp = open(new_filename, 'wb')
 
            while not recvd_size == filesize:
                if filesize - recvd_size > 1024:
                    data = sock.recv(1024)
                    recvd_size += len(data)
                else:
                    data = sock.recv(1024)
                    recvd_size = filesize
                fp.write(data)
            fp.close()
            print('Received img')
            img = cv2.imread("img.jpg")
            cv2.imshow('detect', img)
            cv2.waitKey(20)
        # sock.close()
        break
 
 
if __name__ == '__main__':
    socket_service()