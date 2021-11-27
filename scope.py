# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 15:32:48 2021
实现了交互式加载图片
@author: songfangteng521
"""


import cv2
import numpy as np

import tkinter
import tkinter.filedialog

# 全局变量
g_window_name = "image"  # 窗口名
g_window_wh = [1900, 1000]  # 窗口宽高

g_location_win = [0, 0]  # 相对于大图，窗口在图片中的位置
location_win = [0, 0]  # 鼠标左键点击时，暂存g_location_win
g_location_click, g_location_release = [0, 0], [0, 0]  # 相对于窗口，鼠标左键点击和释放的位置

g_zoom, g_step = 1, 0.1  # 图片缩放比例和缩放系数
"""
图片加载
"""
win = tkinter.Tk()
win.title("picture process")
win.geometry('0x0+999999+0')
select_file = tkinter.filedialog.askopenfilename(title='选择图片')
path = select_file.split('/')[-2]+'/'+select_file.split('/')[-1]
path_3 = select_file.split('/')[-2]+"/3_"+select_file.split('/')[-1]
g_image_original = cv2.imread(path,-1)
g_image_original_3 = cv2.imread(path_3)
win.destroy()

# ret1,g_image_original = cv2.threshold(img,125,65535,cv2.THRESH_BINARY)
# g_image_original=cv2.transpose(g_image_original)
g_image_zoom = g_image_original.copy()  # 缩放后的图片
g_image_zoom_3 = g_image_original_3.copy() 
g_image_show = g_image_original[g_location_win[1]:g_location_win[1] + g_window_wh[1], 
                                g_location_win[0]:g_location_win[0] + g_window_wh[0]]  # 实际显示的图片

g_image_show_3 = g_image_original[g_location_win[1]:g_location_win[1] + g_window_wh[1], 
                                g_location_win[0]:g_location_win[0] + g_window_wh[0]]

a = []
b = []
g_x = 0
g_y = 0
point1=[]
point2=[]
point3=[]
point4=[]
count = 1
ori_image = []
ori_image_3 = []

# 矫正窗口在图片中的位置
# img_wh:图片的宽高, win_wh:窗口的宽高, win_xy:窗口在图片的位置
def check_location(img_wh, win_wh, win_xy):
    for i in range(2):
        if win_xy[i] < 0:
            win_xy[i] = 0
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] > win_wh[i]:
            win_xy[i] = img_wh[i] - win_wh[i]
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] < win_wh[i]:
            win_xy[i] = 0
    # print(img_wh, win_wh, win_xy)


# 计算缩放倍数
# flag：鼠标滚轮上移或下移的标识, step：缩放系数，滚轮每步缩放0.1, zoom：缩放倍数
def count_zoom(flag, step, zoom):
    if flag > 0:  # 滚轮上移
        zoom += step
        if zoom > 1 + step * 20:  # 最多只能放大到3倍
            zoom = 1 + step * 20
    else:  # 滚轮下移
        zoom -= step
        if zoom < step:  # 最多只能缩小到0.1倍
            zoom = step
    zoom = round(zoom, 2)  # 取2位有效数字
    return zoom


# OpenCV鼠标事件
def mouse(event, x, y, flags, param):
    global g_location_click, g_location_release, g_image_show, g_image_zoom, g_image_zoom_3, g_image_show_3, g_location_win, location_win, g_zoom
    global g_x, g_y, point1, point2, point3, point4, count, ori_image_3, ori_image
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        g_location_click = [x, y]  # 左键点击时，鼠标相对于窗口的坐标
        location_win = [g_location_win[0], g_location_win[1]]  # 窗口相对于图片的坐标，不能写成location_win = g_location_win
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        g_location_release = [x, y]  # 左键拖曳时，鼠标相对于窗口的坐标
        h1, w1 = g_image_zoom.shape[0:2]  # 缩放图片的宽高
        w2, h2 = g_window_wh  # 窗口的宽高
        show_wh = [0, 0]  # 实际显示图片的宽高
        if w1 < w2 and h1 < h2:  # 图片的宽高小于窗口宽高，无法移动
            show_wh = [w1, h1]
            g_location_win = [0, 0]
        elif w1 >= w2 and h1 < h2:  # 图片的宽度大于窗口的宽度，可左右移动
            show_wh = [w2, h1]
            g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
        elif w1 < w2 and h1 >= h2:  # 图片的高度大于窗口的高度，可上下移动
            show_wh = [w1, h2]
            g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
        else:  # 图片的宽高大于窗口宽高，可左右上下移动
            show_wh = [w2, h2]
            g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
            g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
        check_location([w1, h1], [w2, h2], g_location_win)  # 矫正窗口在图片中的位置
        g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + show_wh[1], 
                                    g_location_win[0]:g_location_win[0] + show_wh[0]]  # 实际显示的图片
        g_image_show_3 = g_image_zoom_3[g_location_win[1]:g_location_win[1] + show_wh[1], 
                                    g_location_win[0]:g_location_win[0] + show_wh[0]] 
        
    elif event == cv2.EVENT_MOUSEWHEEL:  # 滚轮
        z = g_zoom  # 缩放前的缩放倍数，用于计算缩放后窗口在图片中的位置
        g_zoom = count_zoom(flags, g_step, g_zoom)  # 计算缩放倍数
        w1, h1 = [int(g_image_original.shape[1] * g_zoom), int(g_image_original.shape[0] * g_zoom)]  # 缩放图片的宽高
        w2, h2 = g_window_wh  # 窗口的宽高
        g_image_zoom = cv2.resize(g_image_original, (w1, h1), interpolation=cv2.INTER_AREA)  # 图片缩放
        g_image_zoom_3 = cv2.resize(g_image_original_3, (w1, h1), interpolation=cv2.INTER_AREA)
        show_wh = [0, 0]  # 实际显示图片的宽高
        if w1 < w2 and h1 < h2:  # 缩放后，图片宽高小于窗口宽高
            show_wh = [w1, h1]
            cv2.resizeWindow(g_window_name, w1, h1)
        elif w1 >= w2 and h1 < h2:  # 缩放后，图片高度小于窗口高度
            show_wh = [w2, h1]
            cv2.resizeWindow(g_window_name, w2, h1)
        elif w1 < w2 and h1 >= h2:  # 缩放后，图片宽度小于窗口宽度
            show_wh = [w1, h2]
            cv2.resizeWindow(g_window_name, w1, h2)
        else:  # 缩放后，图片宽高大于窗口宽高
            show_wh = [w2, h2]
            cv2.resizeWindow(g_window_name, w2, h2)
        g_location_win = [int((g_location_win[0] + x) * g_zoom / z - x), int((g_location_win[1] + y) * g_zoom / z - y)]  # 缩放后，窗口在图片的位置
        check_location([w1, h1], [w2, h2], g_location_win)  # 矫正窗口在图片中的位置
        # print(g_location_win, show_wh)
        g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + show_wh[1], g_location_win[0]:g_location_win[0] 
                                    + show_wh[0]]  # 实际的显示图片
        g_image_show_3 = g_image_zoom_3[g_location_win[1]:g_location_win[1] + show_wh[1], g_location_win[0]:g_location_win[0] 
                                    + show_wh[0]]  # 实际的显示图片
        ori_image_3 = g_image_show_3.copy()
    
    elif event == cv2.EVENT_RBUTTONDOWN:#右键点击
        point3 = (x,y)
        cv2.circle(g_image_show_3, point3, 2, (0,255,0), 2)
        # cv2.imshow('img', g_image_zoom)
    # elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_RBUTTON):#右键拖曳 
    #     cv2.rectangle(ori_image, point3, (x,y), (255,0,0), 1)
    #     cv2.imshow('image', ori_image)
    elif event == cv2.EVENT_RBUTTONUP:#右键释放
        point4 = (x,y)
        cv2.rectangle(ori_image_3, point3, point4, (0,0,255), 1) 
        cut_img = g_image_show[point3[1]:point4[1], point3[0]:point4[0]]
        cut_img_3 = g_image_show_3[point3[1]:point4[1], point3[0]:point4[0]]
        # cimg = np.zeros_like(cut_img)
        # print(cimg[0]) 
        # pts = np.where(cimg == 65535)
        
        # cut_img = img[pts[0],pts[1]]
        # cut_img = g_image_show[point4[1]:point3[1], point4[0]:point3[0]]
        cv2.imshow("cut_img",cut_img)
        cv2.imshow("crop_img",cut_img_3)
        cv2.imwrite('ROI{}.png'.format(count), cut_img)   
        cv2.imwrite('3_ROI{}.png'.format(count), cut_img_3) 
        count = count + 1
    # elif event == cv2.EVENT_MBUTTONDOWN:
        
    cv2.imshow(g_window_name, g_image_show_3)

# 主函数
if __name__ == "__main__":
    # 设置窗口
    cv2.namedWindow(g_window_name, cv2.WINDOW_NORMAL)
    # 设置窗口大小，只有当图片大于窗口时才能移动图片
    cv2.resizeWindow(g_window_name, g_window_wh[0], g_window_wh[1])
    cv2.moveWindow(g_window_name, 700, 100)  # 设置窗口在电脑屏幕中的位置
    # 鼠标事件的回调函数
    cv2.setMouseCallback(g_window_name, mouse)
    cv2.waitKey()  # 不可缺少，用于刷新图片，等待鼠标操作
    cv2.destroyAllWindows()

