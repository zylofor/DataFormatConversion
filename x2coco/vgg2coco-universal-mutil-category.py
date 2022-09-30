import os
import json
import re
import cv2
import numpy as np

def get_polygon_structure_properties(shapes):
    x = shapes['all_points_x']
    y = shapes['all_points_y']

    points = []
    contour = []
    for i, val in enumerate(x):
        points.append(val)
        points.append(y[i])
        contour.append([val, y[i]])

    #通过轮廓获取最小外接矩形
    ctr = np.array(contour).reshape((-1, 1, 2)).astype(np.int32)

    area = cv2.contourArea(ctr)
    rect = cv2.boundingRect(ctr)
    x, y, w, h = rect
    bbox = [x, y, w, h]

    return points, bbox, area

def get_rectangle_structure_properties(shapes):
    x = shapes["x"]
    y = shapes["y"]
    w = shapes["width"]
    h = shapes["height"]
    bbox = [x,y,w,h]
    points = [x,y,x,y+h,x+w,y+h,x+w,y]
    ctr = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
    area = cv2.contourArea(ctr)
    return points,bbox,area

def via_to_coco(infile,outfile,image_path):
    via_json = open(infile)
    via_json = json.load(via_json)

    #获取VIA文件的key值
    via_dict_key = list(via_json.keys())

    #创建coco数据集字典
    main_dict = {}

    # 增加info字段信息
    info = "{'date': 2022.4.8, 'version': '3.0','contributor': 'Jiang.Z.Y'}"
    main_dict["info"] = info

    #增加images字段信息
    images = []

    for i, file_name in enumerate(via_json["_via_img_metadata"].keys()):
        image_info = {}

        # x.jpg
        fileName = via_json["_via_img_metadata"][file_name]["filename"]
        file_path = os.path.join(image_path,fileName)

        #获取图像信息
        im = cv2.imread(file_path)
        h,w,c = im.shape
        image_info['id'] = i
        image_info['width'] = w
        image_info['height'] = h
        image_info['file_name'] = fileName
        image_info['coco_url'] = "https://{}".format(fileName)
        images.append(image_info)

    main_dict['images'] = images
    print(main_dict)

    #增加annotations字段信息
    annotations = []
    instance_id = 0

    # 构建类别列表
    cateList = []
    categories = []
    cate_id_num = 1
    dict_label = {}

    for image_id , p  in enumerate(via_json["_via_img_metadata"].keys()):
        regions = via_json["_via_img_metadata"][p]["regions"]

        for k, q in enumerate(regions):

            shape_attributes = q["shape_attributes"]
            region_attributes = q["region_attributes"]

            for label in region_attributes.values():

                if len(region_attributes.values()) != 1 :
                    print("region_attributes len is {}-------> Error!".format(regions["shape_attributes"]["name"]))
                    break

                # 根据不同的区域属性来获取coco字典信息
                if q["shape_attributes"]["name"] == "polygon":
                    segementation,bbox,area = get_polygon_structure_properties(shape_attributes)
                elif q["shape_attributes"]["name"] == "rect":
                    segementation,bbox,area = get_rectangle_structure_properties(shape_attributes)
                else:
                    print("shape_attributes is {}-------> Error!".format(q["shape_attributes"]["name"]))
                    break

                ann = {}
                ann["id"] = instance_id
                ann["image_id"] = image_id

                if int(label) not in cateList:
                    dict_label["{}".format(label)] = cate_id_num
                    cate_id_num += 1

                for key in dict_label.keys():
                    if int(label) == int(key):
                        ann["category_id"] = dict_label[key]

                cateList.append(int(label))
                ann["segmentation"] = [segementation]
                ann["area"] = area
                ann["bbox"] = bbox
                ann["iscrowd"] = 0
                instance_id += 1
                annotations.append(ann)

    print(dict_label)
    main_dict["annotations"] = annotations


    for i , cate_id in enumerate(dict_label):
        cat = {}
        cat["supercategory"] = "WorkPieces"
        cat["id"] = dict_label[cate_id]
        cat["name"] = cate_id
        categories.append(cat)

    main_dict["categories"] = categories

    (filepath, fullname) = os.path.split(outfile)
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    json.dump(main_dict, open(outfile, 'w',encoding='utf-8'), ensure_ascii=False, indent=2)  # indent=2 更加美观显示


if __name__ == '__main__':
    root = "/home/jzy/MyMountDisk/zylofor/SteelDataset/WorkPiecesDataTrans"
    Data_Trans_VIA_Folder = "NeedToTransAnn"
    out_Folder = "output"
    imgs_Folder = "imgs"

    for viaFolderName in os.listdir(os.path.join(root,Data_Trans_VIA_Folder)):
        via_json_file = os.path.join(root,Data_Trans_VIA_Folder + '/' + viaFolderName)
        output_coco_json_file_path = os.path.join(root, out_Folder + '/' + viaFolderName.split('.')[0] + '.json')
        path_images = os.path.join(root, imgs_Folder + '/' + viaFolderName.split('.')[0])
        via_to_coco(via_json_file,output_coco_json_file_path,path_images)