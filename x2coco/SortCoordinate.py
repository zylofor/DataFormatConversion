# -*- coding: utf-8 -*-
from scipy.spatial import distance as dist
import numpy as np
import math
import cv2
from PIL import Image
from pylab import *

def sortCoordinate_four(box):
    '''
    :param box: x,y坐标共4点8值;[x1, y1, x2, y2, x3, y3, x4, y4]
    '''

    x1, y1, x2, y2, x3, y3, x4, y4 = box[:8]
    newBox = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    # 按第2维度正序排序
    newBox = sorted(newBox, key=lambda x: x[1], reverse=False)
    # 按第1维排序，使得x_min最小的在前面
    x1, y1 = sorted(newBox[:2], key=lambda x: x[1])[0]

    index = newBox.index([x1, y1])  # 取出(x_min,y_min)
    newBox.pop(index)

    newBox = sorted(newBox, key=lambda x: x[1], reverse=True)
    x4, y4 = sorted(newBox[:2], key=lambda x: x[0])[0]
    index = newBox.index([x4, y4])
    newBox.pop(index)

    newBox = sorted(newBox, key=lambda x: x[0], reverse=True)
    x2, y2 = sorted(newBox[:2], key=lambda x: x[1])[0]
    index = newBox.index([x2, y2])
    newBox.pop(index)

    newBox = sorted(newBox, key=lambda x: x[1], reverse=True)
    x3, y3 = sorted(newBox[:2], key=lambda x: x[0])[0]

    res = [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]

    if res[0][0] > res[1][0]:
        res[0][0],res[0][1],res[1][0],res[1][1] = res[1][0],res[1][1],res[0][0],res[0][1]

    if res[3][0] > res[2][0]:
        res[3][0], res[3][1], res[2][0], res[2][1] = res[2][0], res[2][1], res[3][0], res[3][1]

    return res

def get_minAreaRect(box):
    cnt = box
    cnt = np.float32(cnt)

    rect = cv2.minAreaRect(cnt)
    rect_coordinate = cv2.boxPoints(rect)
    new_box = np.int0(rect_coordinate)
    x1, y1, x2, y2, x3, y3, x4, y4 = new_box[0][0], new_box[0][1], new_box[1][0], new_box[1][1], new_box[2][0],new_box[2][1], new_box[3][0], new_box[3][1]

    new_box = [x1, y1, x2, y2, x3, y3, x4, y4]

    return new_box


def get_angle(box):
    global angle
    box2 = box

    if box2[3][0] - box2[0][0] == 0:
        k1 = 90
    else:

        k1 = (box2[3][1] - box2[0][1]) / (box2[3][0] - box2[0][0])
        # k = math.fabs((box2[3][1] - box2[0][1]) / (box2[3][0] - box2[0][0]))

    if k1 != 90:
        # alpha = (np.arctan(k) * 180)/math.pi
        alpha = (np.arctan(k1) * 180)/math.pi
    else:
        alpha= 0

    if alpha == 0:
        angle = 0
    else:
        if alpha > 90:
            angle = alpha - 90
        else:
            angle = 90 - alpha



    angle = round(angle,3)




    return angle

# testdata = [1717,1526,1721,1700,1809,1967,1806,1000]
# rec = sortCoordinate_four(testdata)
# print(rec)
# print(rec[1][1])
# angle = get_angle(rec)
# print(angle)
#
# testdata2 = [(1075,931),(1191,911),(1269,1413),(1234,1415),(1140,1403),(1143,1405)]
# new_box = get_minAreaRect(testdata2)
# # rec2 = sortCoordinate_four(new_box)
# # angle = get_angle(rec2)
#
# print(new_box)
# rec = sortCoordinate_four(new_box)
# print(rec)
# angle = get_angle(rec)
# print("angle is {}".format(angle))



