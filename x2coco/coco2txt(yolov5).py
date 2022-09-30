import json
import numpy as np
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import os
# -----------------
# txt数据格式：path，xmin,ymin,xmax,ymax
# 每一行表示一个image
# --------------------

filename = '/home/lab315/jzy/PaperLearning/MyUbuntu/YoloX-based-on-Swin-Transformer-master/coco/annotations/instances_train2017.json'
# filename = '/home/jzy/PaperLearning/MyUbuntu/yolor/data/coco/labels/train2017/train.json'

f = open(filename,encoding='utf-8')
res = f.read()
data = json.loads(res)
# 数据集共90个类
# 保存数据的文件夹
folder = filename.split('.')[0]+'_txt'
if not os.path.exists(folder):
    os.mkdir(folder)

# 首先得到数据的categories的关键字
category = data['categories']
category_id ={}
for category_per in category:
    id = category_per['id']
    cls = category_per['name']
    category_id[id] = cls

print(category_id)
# 开始遍历字典，对每一个图像生成xml文件
imageID_all =[]
imageID_all_info = {}
for images_attr in list(data.keys()):
    if  images_attr == 'images':
        # 遍历每一个图像
        for data_per in data[images_attr]:
            # 获取图像名字
            image_name = data_per['file_name']
            # 获取图像路径
            image_route = data_per['coco_url']
            # 获取图像的像素和ID
            image_width = data_per['width']
            image_height = data_per['height']
            image_id = data_per['id']
            imageID_all.append(image_id)
            imageID_all_info[image_id]={'width':image_width,'height':image_height,'path':image_route,'filename':image_name}

    elif images_attr == 'annotations':
        # 根据id遍历每张图像的bounding box
        for imageID_per in imageID_all:
            print(imageID_per)
            # 根据图像ID，构建图像基本信息子目录
            # 图像路径
            image_path = imageID_all_info[imageID_per]['path']
            # 每一张图片信息写在txt文件
            # filename1 = imageID_all_info[imageID_per]['filename'].split('.')[0]
            file_write = folder + '/' + image_path.split('.')[0].split('//')[-1] + '.txt'
            # 图像包含了多少个bounding box
            boundingBox_image = [j for j in data[images_attr] if j['image_id']==imageID_per]
            boundingBox_cord =''
            # 输出每张boundging box的坐标信息，以及所属类信息
            for boundingBox_per in boundingBox_image:
                # 添加boundingBox所属类的id
                id = boundingBox_per['category_id'] - 1
                # 位置信息转换，x,y,w,h转为xmin,ymin,xmax,ymax
                x = boundingBox_per['bbox'][0]
                y = boundingBox_per['bbox'][1]
                w = boundingBox_per['bbox'][2]
                h = boundingBox_per['bbox'][3]

                img_w = imageID_all_info[boundingBox_per["image_id"]]["width"]
                img_h = imageID_all_info[boundingBox_per["image_id"]]["height"]

                if round(x/img_w,6) < 0:
                    lx = str(0)
                elif round(x / img_w, 6) > 1:
                    lx = str(1)
                else:
                    lx = str(round(x/img_w,6))

                if round((x+w)/img_w,6) < 0:
                    rx = str(0)
                elif round((x+w)/img_w,6) > 1:
                    rx = str(1)
                else:
                    rx = str(round((x+w)/img_w,6))

                if round(y/img_h,6) < 0:
                    ty = str(0)
                elif round(y/img_h,6) > 1:
                    ty = str(1)
                else:
                    ty = str(round(y/img_h,6))

                if round((y+h)/img_h,6) < 0:
                    by = str(0)
                elif round((y+h)/img_h,6) > 1:
                    by = str(1)
                else:
                    by = str(round((y+h)/img_h,6))




                #Normalization

                boundingBox_cord += str(id)+' '+ lx +' '+ ty + ' '+ rx +' '+ by + '\n'

            boundingBox_cord = boundingBox_cord.rstrip()

            with open(file_write, 'a+') as f:
                f.write(boundingBox_cord)