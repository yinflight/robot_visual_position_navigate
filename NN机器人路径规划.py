
'''
//抖音爆改车间主任开源代码
//NN机器人上位机源码
//python3 + openCV 环境
//需要一个USB摄像头俯拍桌面
//先输入机器人IP地址在运行代码
//上位机需要和机器人在同一路由下
//转载保留爆改车间主任署名
//关注“爆改车间”微信公众号获取主任更多开关代码
//关注“爆改车间主任”抖音观看主任最新有趣视频

'''

import cv2 
import numpy as np 
import socket
import math
import numpy as np

BUFSIZE = 1024
client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ip_port = ('192.168.2.218', 1234)  #输入机器人IP地址


n = 199
Mx = 0
My = 0
Point = []
sta = True

def nothing(x):
    pass
def createbars():
    cv2.createTrackbar("n","image",n,250,nothing) 

def get_angle_by_cos(p0, p1, p2): #弧度计算
    """
    使用向量的点乘公式计算角度值
    :param p0:
    :param p1: 角的顶点
    :param p2:
    :return: 弧度
    """
    # print(p0, p1, p2)
    l1 = p0[0] - p1[0], p0[1] - p1[1]
    l2 = p2[0] - p1[0], p2[1] - p1[1]
    # print(l1, l2)
    m = math.sqrt(l1[0] ** 2 + l1[1] ** 2) * math.sqrt(l2[0] ** 2 + l2[1] ** 2)
    if m == 0:
        return 0
    cos = (l1[0] * l2[0] + l1[1] * l2[1]) / m
    # print(cos)
    
    try:
        R = math.acos(cos)
    except:
        R = 180
    return R

def length(p0,p1):  #线段长度计算
    d_x = abs(p0[0]-p1[0])
    d_y = abs(p0[1]-p1[1])
    length_p = math.sqrt(d_x**2 + d_y**2)
    return length_p

def longline(t):    #直角三角形找直角边的长边
    angle = []
    tt = []
    angle.append(get_angle_by_cos(t[0][0],t[1][0],t[2][0]))
    angle.append(get_angle_by_cos(t[1][0],t[2][0],t[0][0]))
    angle.append(get_angle_by_cos(t[2][0],t[0][0],t[1][0]))

    angle[0]  = round(math.degrees(angle[0] ), 2)
    angle[1]  = round(math.degrees(angle[1] ), 2)
    angle[2]  = round(math.degrees(angle[2] ), 2)

    max_angle = angle.index(max(angle))

    if max_angle == 0:
        if length(t[1][0],t[0][0]) > length(t[1][0],t[2][0]):
            tt.append(triangle[1][0])
            tt.append(triangle[0][0])
            tt.append(triangle[2][0])
        else:
            tt.append(triangle[1][0])
            tt.append(triangle[2][0])
            tt.append(triangle[0][0])
    elif max_angle == 1:
        if length(triangle[2][0],triangle[0][0]) > length(triangle[2][0],triangle[1][0]):
            tt.append(triangle[2][0])
            tt.append(triangle[0][0])
            tt.append(triangle[1][0])
        else:
            tt.append(triangle[2][0])
            tt.append(triangle[1][0])
            tt.append(triangle[0][0])
    elif max_angle == 2:
        if length(triangle[0][0],triangle[1][0]) > length(triangle[0][0],triangle[2][0]):
            tt.append(triangle[0][0])
            tt.append(triangle[1][0])
            tt.append(triangle[2][0])
        else:
            tt.append(triangle[0][0])
            tt.append(triangle[2][0])
            tt.append(triangle[1][0])
    return tt


def setpoint(event,x,y,flags,param):  #鼠标点击位置

    global Point
    if event==cv2.EVENT_LBUTTONDOWN:
        print("Point is",x,y)
        Point.append((x,y))
        print(Point)
    if event==cv2.EVENT_RBUTTONDOWN:
        Point = []
    


camera = cv2.VideoCapture(0) # 参数0表示第一个摄像头 
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# 判断视频是否打开 
if (camera.isOpened()):
    print('Open') 
else: 
    print('摄像头未打开') 

cv2.namedWindow("image",cv2.WINDOW_NORMAL)
createbars()

while True:
    grabbed, frame_lwpCV = camera.read() 
    #cv2.imshow('contours', frame_lwpCV) 
    frame_lwpCV = cv2.GaussianBlur(frame_lwpCV, (3, 3), 0) #高斯模糊
    frame_gray = cv2.cvtColor(frame_lwpCV,cv2.COLOR_BGR2GRAY)
    n=cv2.getTrackbarPos("n","image")#获取"n"滑块的实时值
    ret,binary = cv2.threshold(frame_gray,n,255,cv2.THRESH_BINARY) #二值化
    #cv2.imshow("binary",binary)

    contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #获取轮廓

    level = 0
    contours_sign = []
    #print(hierarchy)
    

    for i in range(len(hierarchy[0])):   #查找三层轮廓
        hie = hierarchy[0][i]
        if hie[2] != -1:
            level += 1
            pass
        elif hie[2] == -1 and level != 0:
            level += 1
            if level == 3:
                #print("三层")
                #print(cv2.contourArea(contours[i])/cv2.contourArea(contours[i-1]))
                if 0.1 < (cv2.contourArea(contours[i])/cv2.contourArea(contours[i-1])) <0.5:
                    contours_sign.append(contours[i-1])
                pass
            level = 0
            pass
        else:
            level = 0



    cv2.drawContours(frame_lwpCV,contours_sign,-1,(0,0,255),2) #绘制轮廓
    
    if len(contours_sign) !=0:
        retval, triangle = cv2.minEnclosingTriangle(contours_sign[0])
        triangle = np.int0(triangle)
        #cv2.polylines(frame_lwpCV,[triangle], True, (255,0,0),2)  #绘制轮廓最小三角形

        line = longline(triangle)    #找到直角边的长边作为机器人的y轴

        D = ((line[1][0]+line[2][0]-line[0][0]),(line[1][1]+line[2][1]-line[0][1]))
        line.append(D)

        # cv2.line(frame_lwpCV,line[2],line[3],(0,0,255),2) 

        # cv2.line(frame_lwpCV,line[0],line[1],(0,0,255),2) 

        Nx1 = int((abs(line[0][0]-line[2][0]))/2+min(line[0][0],line[2][0]))
        Ny1 = int((abs(line[0][1]-line[2][1]))/2+min(line[0][1],line[2][1]))
        Nx  = int((abs(line[1][0]-line[3][0]))/2+min(line[1][0],line[3][0]))
        Ny  = int((abs(line[1][1]-line[3][1]))/2+min(line[1][1],line[3][1]))
        Nx  = int((abs(Nx-Nx1))/2+min(Nx,Nx1))
        Ny  = int((abs(Ny-Ny1))/2+min(Ny,Ny1))
        #print(Nx,Ny,Nx1,Ny)

        cv2.line(frame_lwpCV,(Nx1,Ny1),(Nx,Ny),(0,0,255),2) 


    if len(Point) != 0:
        cv2.line(frame_lwpCV,(Nx,Ny),Point[0],(0,0,255),2)
        if(len(Point)) > 1:
            for j in range(len(Point)-1):
                cv2.line(frame_lwpCV,Point[j],Point[j+1],(0,0,255),2)
        Mx = Point[0][0]
        My = Point[0][1]
    else:
        Mx = 0
        My = 0



    if Mx !=0 and My !=0:    #处理三个点的数据，机器人y轴线两个点line，鼠标单击的点Mx，My
        cv2.line(frame_lwpCV,(Nx,Ny),(Mx,My),(0,0,255),2)

        a = get_angle_by_cos((Nx1,Ny1),(Nx,Ny),(Mx,My))  #计算机器人与目标点的弧度
        b = ((Mx-Nx1)*(Ny-Ny1))-((My-Ny1)*(Nx-Nx1))  #计算机器人方向
        angle = round(math.degrees(a), 2)  #计算机器人与目标点角度
        #print(f"弧度：{a}， 角度：{angle} , 方向: {b}")
        N_M = length((Nx,Ny),(Mx,My))  #机器人与目标点距离
        font=cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame_lwpCV,str(int(N_M)),(Nx,Ny),font,1,(0,0,255),2)

        if N_M > 25 :
            msg = "C"+str(int(N_M))+",R"+str(int(angle))+",F"+str(b)
            client.sendto(msg.encode('utf-8'),ip_port)   #UDP发送数据
        if N_M <=25 :
            if len(Point) != 0:
                Point.remove(Point[0])
                print(Point)
            else:
                Mx = 0 
                My = 0
    else:
        msg = "C0,R180,F1"
        client.sendto(msg.encode('utf-8'),ip_port)   #UDP发送数据
    

        
    if sta:
        cv2.imshow("frame",frame_lwpCV)
    else:
        cv2.imshow("frame",binary)
    cv2.setMouseCallback("frame",setpoint)


    key = cv2.waitKey(1) & 0xFF 
    # 按'q'健退出循环 
    if key == ord('q'):
        break 
    if key == ord('p'):
        sta = not sta
        print(sta)

camera.release() 
cv2.destroyAllWindows() 