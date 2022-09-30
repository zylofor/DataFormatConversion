#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os, cv2
import numpy as np
from datetime import datetime
import math
from SortCoordinate import sortCoordinate_four,get_angle,get_minAreaRect


# In[ ]:

##add rotate angle of bbox

def get_structure_properties(shapes):
    global angle
    print(shapes)
    x = shapes['all_points_x']
    ##TODO:Starting rotate transfors.

    y = shapes['all_points_y']

    points = []
    contour = []
    for i, val in enumerate(x):
        points.append(val)
        points.append(y[i])
        contour.append([val, y[i]])


    #   TODO:add function
        Rectpoints = get_minAreaRect(contour)
        sortpoints = sortCoordinate_four(Rectpoints)
        angle = get_angle(sortpoints)

    ctr = np.array(contour).reshape((-1, 1, 2)).astype(np.int32)
    area = cv2.contourArea(ctr)
    rect = cv2.boundingRect(ctr)
    x, y, w, h = rect
    x1,y1,w,h = x+0.5*w,y+0.5*h,w,h
    bbox = [x1, y1, w, h, angle]

    return points, bbox, area


# In[ ]:


def via_to_coco(infile, outfile, image_path):
    vgg_json = open(infile)
    vgg_json = json.load(vgg_json)

    main_dict = {}
    info = "{'year': 2021, 'version': '3', 'description': 'Exported using VGG Image Annotator (http://www.robots.ox.ac.uk/~vgg/software/via/)', 'contributor': '', 'url': 'http://www.robots.ox.ac.uk/~vgg/software/via/', 'date_created': 'Sun Mar 28 2021 21:50:26 GMT+0100 (Central European Standard Time)'}"
    image_list = list(vgg_json.keys())

    images = []

    for i, img in enumerate(vgg_json['_via_img_metadata']):
        image = {}
        #print(vgg_json[img])
        (filepath,fullname) = os.path.split(img)
        (filename,extension) = os.path.splitext(fullname)
        if len(extension) > len(".jpg"):
            im = cv2.imread(os.path.join(image_path,filename+".jpg"))
        else:
            im = cv2.imread(os.path.join(image_path,img))
        h, w, c = im.shape
        image['id'] = i
        image['width'] = w
        image['height'] = h
        image['file_name'] = ("%s.jpg" % filename)
        image['coco_url'] = ("%s.jpg" % filename)
        images.append(image)

    annotations = []
    image_id = 0
    for i, v in enumerate(vgg_json["_via_img_metadata"]):
        (filepath,fullname) = os.path.split(v)
        (filename,extension) = os.path.splitext(fullname)

        data = vgg_json["_via_img_metadata"][v]
        regions = data["regions"]
        for j, r in enumerate(regions):
            print(regions)
            print(len(regions))
            shape_attributes = r["shape_attributes"]


            if len(shape_attributes) != 3:
                break
            region_attributes = r["region_attributes"]
            objekt = 'antenna'

            segmentation, bbox, area = get_structure_properties(shape_attributes)
            anno = {}
            anno['id'] = image_id
            anno['image_id'] = i
            anno['category_id'] = 1
            anno['segmentation'] = segmentation
            anno['area'] = area
            anno['bbox'] = bbox
            anno['iscrowd'] = 0
            image_id += 1
            annotations.append(anno)

    main_dict['info'] = info
    main_dict['images'] = images
    main_dict['annotations'] = annotations
    main_dict['categories'] = [{"id": 1,"name": "antenna"}]
    (filepath, fullname) = os.path.split(outfile)
    (filename, extension) = os.path.splitext(fullname)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    json.dump(main_dict, open(outfile, 'w',encoding='utf-8'), ensure_ascii=False, indent=2)  # indent=2 更加美观显示
    # with open(outfile, 'w') as f:
    #     json.dump(main_dict, f, ensure_ascii=False, indent=2)  # indent=2 更加美观显示
    #     f.close()


# In[ ]:


if __name__ == '__main__':
    vocFolderName = "3"
    vgg_json_file = "/home/jzy/MyMountDisk/zylofor/SteelDataset/Steel/%s/%s" %(vocFolderName, "3.json")   # path_to_input_via_json_file
    saved_time = format(datetime.now(), "%Y%m%d%H%M%S")
    cocoFolderName = saved_time
    json_file = ('/home/jzy/MyMountDisk/zylofor/SteelDataset/Steel/3/%s/instances_train%s.json' % (cocoFolderName, cocoFolderName))  # path_to_output_coco_json_file
    path_images = "/home/jzy/MyMountDisk/zylofor/SteelDataset/Steel/3" # path_to_images
    via_to_coco(vgg_json_file, json_file, path_images)

