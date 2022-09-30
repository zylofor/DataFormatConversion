#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os, cv2
import numpy as np
from datetime import datetime
import math
import re


def get_structure_properties(shapes):
    x = shapes['all_points_x']
    y = shapes['all_points_y']

    points = []
    contour = []
    for i, val in enumerate(x):
        points.append(val)
        points.append(y[i])
        contour.append([val, y[i]])


    ctr = np.array(contour).reshape((-1, 1, 2)).astype(np.int32)
    area = cv2.contourArea(ctr)
    rect = cv2.boundingRect(ctr)
    x, y, w, h = rect
    bbox = [x, y, w, h]

    return points, bbox, area

def via_to_coco(infile, outfile, image_path):
    vgg_json = open(infile)
    vgg_json = json.load(vgg_json)

    main_dict = {}
    info = "{'year': 2022, 'version': '2', 'description': 'Exported using VGG Image Annotator (http://www.robots.ox.ac.uk/~vgg/software/via/)', 'contributor': 'Jiang.Z.Y', 'url': 'http://www.robots.ox.ac.uk/~vgg/software/via/', 'date_created': 'Sun Feb 02 2020 11:47:26 GMT+0100 (Central European Standard Time)'}"
    image_list = list(vgg_json.keys())

    images = []

    for i, img in enumerate(vgg_json['_via_img_metadata']):
        image = {}
        #print(vgg_json[img])
        (filepath,fullname) = os.path.split(img)
        (filename,extension) = os.path.splitext(fullname)

        auxFileName = re.split(r'(\d+)', extension)
        if len(extension) > len(".jpg"):
            if auxFileName[0] == '.png':
                im = cv2.imread(os.path.join(image_path, filename + ".png"))
            elif auxFileName[0] == '.jpg':
                im = cv2.imread(os.path.join(image_path, filename + ".jpg"))
            elif auxFileName[0] == '.JPG':
                im = cv2.imread(os.path.join(image_path, filename + ".JPG"))

        h, w, c = im.shape
        image['id'] = i
        image['width'] = w
        image['height'] = h
        image['file_name'] = ("%s%s" % (filename,auxFileName[0]))
        image['coco_url'] =  ("%s%s" % (filename,auxFileName[0]))
        images.append(image)

    annotations = []
    image_id = 0
    for i, v in enumerate(vgg_json["_via_img_metadata"]):
        (filepath,fullname) = os.path.split(v)
        (filename,extension) = os.path.splitext(fullname)

        data = vgg_json["_via_img_metadata"][v]
        regions = data["regions"]

        for j, r in enumerate(regions):
            # print(regions)
            # print(len(regions))
            shape_attributes = r["shape_attributes"]


            if len(shape_attributes) != 3:
                break

            region_attributes = r["region_attributes"]

            superCategories = []

            for key in region_attributes:
                superCategories.append(key[int(key)])

            classLabel = region_attributes[superCategories[0]]

            segmentation, bbox, area = get_structure_properties(shape_attributes)
            anno = {}
            anno['id'] = image_id
            anno['image_id'] = i
            anno['category_id'] = int(classLabel)
            anno['segmentation'] = [segmentation]
            anno['area'] = area
            anno['bbox'] = bbox
            anno['iscrowd'] = 0
            image_id += 1
            annotations.append(anno)

    main_dict['info'] = info
    main_dict['images'] = images
    main_dict['annotations'] = annotations


    main_dict['categories'] = [{"supercategory":"workpieces","id": 1,"name": "0"},
                               {"supercategory":"workpieces","id": 2,"name": "190"}]



    (filepath, fullname) = os.path.split(outfile)
    (filename, extension) = os.path.splitext(fullname)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    json.dump(main_dict, open(outfile, 'w',encoding='utf-8'), ensure_ascii=False, indent=2)  # indent=2 更加美观显示



if __name__ == '__main__':
    root = "/home/jzy/MyMountDisk/zylofor/SteelDataset/WorkPiecesDataTrans"
    Data_Trans_Folder = "NeedToTransAnn"
    out_Folder = "output"
    imgs_Folder = "imgs"

    for VocFolderName in os.listdir(os.path.join(root,Data_Trans_Folder)):
        vgg_json_file = os.path.join(root,Data_Trans_Folder + '/' +VocFolderName)
        # vgg_json_file = "/home/jzy/MyMountDisk/zylofor/AluminiumDataSet/%s/%s" %(vocFolderName, "158-184.json")   # path_to_input_via_json_file
        # json_file = ('/home/jzy/MyMountDisk/zylofor/AluminiumDataSet/%s.json' % (vocFolderName))  # path_to_output_coco_json_file
        # path_images = "/home/jzy/MyMountDisk/zylofor/AluminiumDataSet/158-184" # path_to_images
        output_coco_json_file_path = os.path.join(root,out_Folder + '/' + VocFolderName.split('.')[0] + '.json')
        path_images = os.path.join(root,imgs_Folder)

        via_to_coco(vgg_json_file, output_coco_json_file_path, path_images)

