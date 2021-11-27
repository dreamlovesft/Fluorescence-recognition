# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 17:00:48 2021

@author: songfangteng521
"""
import tkinter
import tkinter.filedialog
import time
import cv2

import numpy as np

blockSize = 31
value = -1

list0 = []
List = []
List_3 = []
listX = []
listY = []
lst_intensities = [] 
lst_intensities_3 = [] 
count = 0

#创建一个界面窗口
win = tkinter.Tk()
win.title("picture process")
win.geometry('0x0+999999+0')
# win.withdraw() ## 将Tkinter.Tk()实例隐藏

#实现在本地电脑选择图片
select_file = tkinter.filedialog.askopenfilename(title='选择图片')
path = select_file.split('/')[-1]
path_3 = "3_"+path.split('.')[0]+".png"
img = cv2.imread(path,-1)
img_3 = cv2.imread(path_3)
win.destroy()

def transfer_16bit_to_8bit(image_16bit):
    min_16bit = np.min(image_16bit)
    max_16bit = np.max(image_16bit)
    # image_8bit = np.array(np.rint((255.0 * (image_16bit - min_16bit)) / float(max_16bit - min_16bit)), dtype=np.uint8)
    # 或者下面一种写法
    image_8bit = np.array(np.rint(255 * ((image_16bit - min_16bit) / (max_16bit - min_16bit))), 
                          dtype=np.uint8)
    return image_8bit


gray = transfer_16bit_to_8bit(img)
gray_3 = cv2.cvtColor(img_3,cv2.COLOR_BGR2GRAY)



#自适应阈值
th4 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv2.THRESH_BINARY, blockSize, value)
th4_3 = cv2.adaptiveThreshold(gray_3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                            cv2.THRESH_BINARY, blockSize, value)

def drawIndex(cX, cY, count, c):
    global img
    global gray
    global gary_3
    global img_3
    cv2.circle(img_3, (cX, cY), 1, (60,201,202), -1)#绘制中心点
    cv2.putText(img_3,'{}'.format(count),(cX, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(19,201,202),1)
    # 获取ROI荧光值
    cimg = np.zeros_like(gray)
    cimg_3 = np.zeros_like(gray_3)
    cv2.drawContours(cimg, [c], 0, 255, -1)
    cv2.drawContours(cimg_3, [c], 0, 255, -1)
    pts = np.where(cimg == 255)
    pts_3 = np.where(cimg_3 == 255)
    lst_intensities.append(img[pts[0], pts[1]])  
    lst_intensities_3.append(img_3[pts_3[0], pts_3[1]])
    # cv2.imshow("1.png",img_3) 
    

contours,hierarchy = cv2.findContours(th4.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
contours_3,hierarchy = cv2.findContours(th4_3.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

# for c in contours_3:
#     t_list = []
#     ares = cv2.contourArea(c)
#     if ares<150:
#         continue
#     M = cv2.moments(c)
#     center_x = int(M["m10"] / M["m00"])
#     center_y = int(M["m01"] / M["m00"])

#     t_list = [center_y-3,center_y-2,center_y-1,center_y,
#               center_y+1,center_y+2,center_y+3]#center_x-4,,center_x+4
#     # 求t_list和listX的交集，若交集为空说明，center_x不在于listX中，可以添加
#     retA = [i for i in t_list if i in listY]
#     if not len(retA):
#         listX.append(center_x)
#         listY.append(center_y)
#         List_3.append([center_x,center_y,c]);
        
for c in contours:
    t_list = []
    ares = cv2.contourArea(c)
    if ares<150:
        continue
    
    M = cv2.moments(c)
    center_x = int(M["m10"] / M["m00"])
    center_y = int(M["m01"] / M["m00"])

    t_list = [center_y-3,center_y-2,center_y-1,center_y,
              center_y+1,center_y+2,center_y+3]#center_x-4,,center_x+4
    # 求t_list和listX的交集，若交集为空说明，center_x不在于listX中，可以添加
    retA = [i for i in t_list if i in listY]
    if not len(retA):
        listX.append(center_x)
        listY.append(center_y)
        List.append([center_x,center_y,c]); 
    
    
# 按center_y(x[1])升序排序，使序号有序
List.sort(key = lambda x : (x[1]))

"""
添加新功能：定位空白位置信息。判断前后center_y的距离差是否大于阈值（该阈值由图片大小决定）
"""    
preX = List[0][0];
preY = List[0][1];


    
for [cX,cY,c] in List:
    count = count + 1
    if(preY != cY):#第一个不用进行判断
        #判断相邻的两个centerX距离是否大于30，
        #大于30说明中间有capture条带没有显示荧光
        if(cY > preY + 28):
            for y in range(preY+14,cY-3,14):#用cX-4代替cX，如果preX+21比较靠近cX的话，两个相邻的count会指向
            #同一个条带
                drawIndex(preX, y, count, np.zeros_like(c))
                count = count+1
    drawIndex(cX, cY, count, c) 
    preX = cX
    preY = cY

cv2.imshow("1.png",img_3) 
cv2.waitKey(0)
for item in lst_intensities:
    #荧光值降序排序
    item = -np.sort(-item)
    #获取前三个最大值
    if(len(item)>3):
        temp_intensities = item[:20] 
    else:
        temp_intensities = np.zeros_like(temp_intensities)
    # intensities = np.average(item)
    list0.append(temp_intensities)
t = time.time()
version = int(t)%10000 


np.set_printoptions(suppress=True)
np.set_printoptions(precision=4) 
np.savetxt("result{}.csv".format(version), list0, delimiter=',',fmt='%.4f')#,fmt='%s'

