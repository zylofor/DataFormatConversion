import os
import json
import cv2
import numpy as np
from PIL import Image
import shutil

def get_polygon_structure_properties(shapes,imgeName):
    x = shapes['all_points_x']
    y = shapes['all_points_y']

    points = []
    contour = []
    for i, val in enumerate(x):
        points.append(val)
        points.append(y[i])
        contour.append([val, y[i]])

    # assert len(points)>4
    if len(points) <= 4:
        print("Shape Error")
        print(imgeName)

    #通过轮廓获取最小外接矩形
    ctr = np.array(contour).reshape((-1, 1, 2)).astype(np.int32)

    area = cv2.contourArea(ctr)
    rect = cv2.boundingRect(ctr)
    x, y, w, h = rect
    bbox = [x, y, w, h]

    return points, bbox, area

def get_rectangle_structure_properties(shapes,imageName):
    x = shapes["x"]
    y = shapes["y"]
    w = shapes["width"]
    h = shapes["height"]
    bbox = [x,y,w,h]
    points = [x,y,x,y+h,x+w,y+h,x+w,y]

    if len(points) <= 4 :
        print(imageName)

    ctr = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
    area = cv2.contourArea(ctr)
    return points,bbox,area


def via_to_coco(infile,outfile,image_path,csvTrans):
    global csv_writer

    via_json = open(infile)
    via_json = json.load(via_json)

    #获取VIA文件的key值
    via_dict_key = list(via_json.keys())

    #创建coco数据集字典
    main_dict = {}

    # 增加info字段信息
    info = "{'date': 2022.4.9, 'version': '3.1','contributor': 'Jiang.Z.Y'，'task': WorkPieces count}"
    main_dict["info"] = info

    #增加images字段信息
    images = []

    for i, file_name in enumerate(via_json["_via_img_metadata"].keys()):
        image_info = {}

        # x.jpg
        fileName = via_json["_via_img_metadata"][file_name]["filename"]
        file_path = os.path.join(image_path,fileName)

        #获取图像信息
        # im = cv2.imread(file_path)
        im = Image.open(file_path)
        
        # if im is None:
        #     print("file_path {} is None".format(file_path))
        #     im = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), 0)
        # 
        #     if im is None:
        #         print("decode fail!")
        #     else:
        #         print("decode successful!")
        

        w,h = im.size
        image_info['id'] = i
        image_info['width'] = w
        image_info['height'] = h
        image_info['file_name'] = fileName
        image_info['coco_url'] = "https://{}".format(fileName)
        images.append(image_info)

    main_dict['images'] = images

    #增加annotations字段信息
    annotations = []
    instance_id = 0

    # 构建类别列表
    cateList = []
    categories = []
    dict_label = {}


    for image_id , p  in enumerate(via_json["_via_img_metadata"].keys()):
        regions = via_json["_via_img_metadata"][p]["regions"]

        for k, q in enumerate(regions):

            shape_attributes = q["shape_attributes"]
            region_attributes = q["region_attributes"]


            for label in region_attributes.values():
                if label is None:
                    print("{} label is None ---> Error!".format(p))

                if len(region_attributes.values()) != 1 :
                    print("region_attributes len is {}-------> Error!".format(regions["shape_attributes"]["name"]))


                # 根据不同的区域属性来获取coco字典信息
                if q["shape_attributes"]["name"] == "polygon":
                    segementation,bbox,area = get_polygon_structure_properties(shape_attributes,p)
                elif q["shape_attributes"]["name"] == "rect":
                    segementation,bbox,area = get_rectangle_structure_properties(shape_attributes,p)
                    # print("shape_attributes is {}-------> Warning!".format(q["shape_attributes"]["name"]))
                    # print(p)
                else:
                    print("shape_attributes is {}-------> Error!".format(q["shape_attributes"]["name"]))
                    print(p)
                    break

                ann = {}
                ann["id"] = instance_id
                ann["image_id"] = image_id

                # print(p)


                if int(label) not in cateList:
                    dict_label["{}".format(int(label))] = int(label)+1


                for key in dict_label.keys():
                    if int(label) == int(key):
                        # TODO：输出多类
                        ann["category_id"] = dict_label[key]

                        # TODO：只输出单类
                        # ann["category_id"] = 1

                cateList.append(int(label))
                ann["segmentation"] = [segementation]
                ann["area"] = area
                ann["bbox"] = bbox

                #拥挤场景设为1
                if ann['image_id'] in [65,71,99,101,181,174]:
                    ann["iscrowd"] = 1
                else:
                    ann["iscrowd"] = 0

                # ann["iscrowd"] = 0
                instance_id += 1
                annotations.append(ann)
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

def combin_coco_json_file(need_combin_FolderName,need_combin_Folder_Path,out_combin_Result_Path):
    #得到每一个json文件的完整路径
    global json_file_raw
    jsonList = []


    #第一个json文件包含的类别
    cateList = [0,190]

    for i, filename in enumerate(need_combin_FolderName):
        jsonList.append(os.path.join(need_combin_Folder_Path,filename))
    print("共有个{}文件需要合并".format(len(jsonList)))
    print(jsonList)
    # 构建字典和增加info字段信息
    main_dict = {}
    info = "{'date': 2022.4.9, 'version': '3.1','contributor': 'Jiang.Z.Y'，'task': WorkPieces count}"
    main_dict["info"] = info

    jsonList.sort(key=lambda x:int(((x.rsplit('/')[-1]).split('.')[0])))
    for j,imagesName in enumerate(jsonList):
        if j == 0:
            json_file_raw = open(jsonList[0])
            json_file_raw = json.load(json_file_raw)

        else:
            json_file_new = open(jsonList[int(j)])
            json_file_new = json.load(json_file_new)

            json_file_raw_images_id_sum = len(json_file_raw["images"])
            for k , images in enumerate(json_file_new["images"]):
                images["id"] = k + json_file_raw_images_id_sum
                print("images[id] is {},k is {},json_file_raw_images_id_sum is {} ".format(images["id"],k,json_file_raw_images_id_sum))
                json_file_raw["images"].append(images)
            main_dict["images"] = sorted(json_file_raw["images"],key=lambda k: k["id"])


            json_file_raw_ann_id_sum = len(json_file_raw["annotations"])
            image_id_list = []
            for k , ann in enumerate(json_file_new["annotations"]):
                ann["id"] = k + json_file_raw_ann_id_sum
                image_id_list.append(ann["image_id"])

                ann["image_id"] = ann["image_id"] + json_file_raw_images_id_sum

                # print("ann[image_id] is {}".format(ann["image_id"]))

                json_file_raw["annotations"].append(ann)

            main_dict["annotations"] = sorted(json_file_raw["annotations"],key=lambda k:k["id"])

            # TODO：输出多类

            json_file_raw_category_id_sum = len(json_file_raw["categories"])
            for k , cate in enumerate(json_file_new["categories"]):
                if int(cate["name"]) not in cateList:
                    # cate["id"]=k + json_file_raw_category_id_sum
                    json_file_raw["categories"].append(cate)
                cateList.append(int(cate["name"]))


            main_dict["categories"] = sorted(json_file_raw["categories"], key=lambda k: k['id'])

            #TODO：只输出单类
            # main_dict['categories'] = [{"supercategory": "workpieces", "id": 1, "name": "steel"}]


            print("第{}次合并完成，共{}张图片，{}个标注框，{}个类别！".format(j,len(main_dict["images"]),
                                                     len(main_dict["annotations"]),
                                                     len(main_dict["categories"])))

    print(main_dict["categories"])
    # print(len(main_dict["images"]))
    if not os.path.exists(out_combin_Result_Path):
        os.makedirs(out_combin_Result_Path)
    json.dump(main_dict, open(os.path.join(out_combin_Result_Path,"combinResults.json"), 'w',encoding='utf-8'), ensure_ascii=False, indent=2)  # indent=2 更加美观显示

def coco2csv(coco_json_path,out_csv_path):
    import csv
    import uuid
    print("------------>开始转换csv文件")

    csv_file_path = os.path.join(out_csv_path,"workpieces-{}.csv".format(uuid.uuid4()))
    csv_file = open((csv_file_path), mode='a',encoding='utf-8', newline='')
    csv_writer = csv.DictWriter(csv_file,
                                fieldnames=['gtbboxid', 'classid', 'imageid', 'lx', 'rx', 'ty', 'by', 'difficult',
                                            'split'])
    csv_writer.writeheader()

    combined_coco_json = open(os.path.join(coco_json_path))
    combined_coco_json = json.load(combined_coco_json)

    annotation = combined_coco_json["annotations"]

    for i , ann in enumerate(annotation):
        #TODO:在列表里添加困难样本类
        if ann['category_id'] in [65,71,99,101,181,174]:
            difficult = 1
        else:
            difficult = 0
        #
        # TODO: 在列表里添加验证类
        # TODO: Level K
        Level1_images_id = [9,10,11,31,32,33,36,64,135,160,168,169,170,179,180,181,182,183,202,203,204,
                               209,210,228,229,230,231,232,233,234,241,242,243,244,245,246,247,249,250,252,
                               253,254,255,256,258,264,265,277,278,300,303,304,305,306,307,308,309,312,315,
                               316,317,318,319,320,321,329,330,331,333,343,344,347,348,356,357,360,366,367,
                               370,624,625,626,627,628,629,630,691,709,710,735,736,777,798,812,818,832,833,
                               847,848,869,886,887,888,889,893,903,931,932,937,972,985,986,987,994,995,996,
                               997,998,1003,1015]

        # print("Level-1 has {} images".format(len(Level1_images_id)))

        Level2_images_id = [27,28,29,30,34,35,37,38,39,40,41,42,43,44,45,46,62,65,66,67,68,69,70,73,74,75,76,77,
                            78,79,80,81,82,83,130,131,132,133,134,159,161,167,237,238,239,240,260,272,273,274,
                            275,310,311,329,342,368,375,460,461,462,463,464,465,466,467,468,469,470,471,472,473,478,479,480,481,497,498,
                            499,500,502,622,623,693,711,712,713,714,882,883,884,963,965,990,1017,1020,1026,
                            1027,1028]

        # print("Level-2 has {} images".format(len(Level2_images_id)))

        Level3_images_id = [84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,130,131,132,133,134,
                             148,149,150,151,152,153,154,155,156,157,158,166,207,224,260,269,270,271,288,296,
                             297,298,299,322,323,324,325,326,327,336,337,338,351,361,362,557,558,676,677,678,
                             679,680,681,682,683,684,685,686,687,688,689,690,692,804,805,806,808,835,836,837,
                             838,839,840,841,842,843,844,933,934,956,962,979,984,1004,1011,1025]

        # print("Level-3 has {} images".format(len(Level3_images_id)))

        Levelk_images_id = [9,10,11,31,32,33,36,64,135,160,168,169,170,179,180,181,182,183,202,203,204,
                            209,210,228,229,230,231,232,233,234,241,242,243,244,245,246,247,249,250,252,
                            253,254,255,256,258,264,265,277,278,300,303,304,305,306,307,308,309,312,315,
                            316,317,318,319,320,321,329,330,331,333,343,344,347,348,356,357,360,366,367,
                            370,624,625,626,627,628,629,630,691,709,710,735,736,777,798,812,818,832,833,
                            847,848,869,886,887,888,889,893,903,931,932,937,972,985,986,987,994,995,996,
                            997,998,1003,1015,27,28,29,30,34,35,37,38,39,40,41,42,43,44,45,46,62,65,66,67,68,69,70,73,74,75,76,77,78,79,80,81,
                            82,83,130,131,132,133,134,159,161,167,237,238,239,240,260,272,273,274,275,310,
                            311,329,342,368,375,460,461,462,463,464,465,466,467,468,469,470,471,472,473,478,
                            479,480,481,497,498,499,500,502,622,623,693,711,712,713,714,882,883,884,963,965,990,1017,1020,1026,
                            1027,1028,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,130,131,132,133,134,
                            148,149,150,151,152,153,154,155,156,157,158,166,207,224,260,269,270,271,288,296,
                            297,298,299,322,323,324,325,326,327,336,337,338,351,361,362,557,558,676,677,678,
                            679,680,681,682,683,684,685,686,687,688,689,690,692,804,805,806,808,835,836,837,
                            838,839,840,841,842,843,844,933,934,956,962,979,984,1004,1011,1025]

        # print("Level-K has {} images".format(len(Levelk_images_id)))


        # #TODO:Split Level1~Level3
        # if ann['image_id'] in Level1_images_id:
        #     split = '1'
        #
        # elif ann['image_id'] in Level2_images_id:
        #     split = '2'
        #
        # elif ann['image_id'] in Level3_images_id:
        #     # pass
        #     split = '3'
        # else:
        #     split = 'train'

        # TODO:Split LevelK
        if ann['image_id'] in Level3_images_id:
            split = '3'

        else:
            split = 'train'


        img_id = ann['image_id']
        # print(img_id)
        img_w = combined_coco_json["images"][img_id]["width"]
        img_h = combined_coco_json["images"][img_id]["height"]

        # print(combined_coco_json["images"][img_id]["coco_url"])
        lx = round(ann["bbox"][0] /img_w,4)
        rx = round((ann["bbox"][0]+ann["bbox"][2])/img_w,4)
        ty = round(ann["bbox"][1] /img_h,4)
        by = round((ann["bbox"][1]+ann["bbox"][3])/img_h,4)

        dic = {  # 字典类型
            'gtbboxid': ann['id'],
            'classid': ann['category_id'] - 1,
            'imageid': ann['image_id'],
            'lx': lx,
            'rx': rx,
            'ty': ty,
            'by': by,
            'difficult': difficult,
            'split': split }
        csv_writer.writerow(dic)  # 数据写入csv文件
    print("csv文件转换完成，输出路径为------>{}".format(csv_file_path))

if __name__ == '__main__':
    root = "/home/lab315/jzy/PaperLearning/MyDatasets/zylofor/SteelDataset/WorkPiecesDataTrans"
    Data_Trans_VIA_Folder = "NeedToTransAnnbk"
    out_Folder = "transResults"
    imgs_Folder = "imgs"
    combinResults = "combinResults"
    json_file_trans = True
    json_file_combin = True
    csvTrans = False
    json_file_dir = os.listdir(os.path.join(root,Data_Trans_VIA_Folder))
    json_file_dir.sort(key=lambda x:int(x.split('.')[0]))


    if json_file_trans is True:
        for num,viaFolderName in enumerate(json_file_dir):
            via_json_file = os.path.join(root,Data_Trans_VIA_Folder + '/' + viaFolderName)
            output_coco_json_dir = os.path.join(root, out_Folder)
            output_coco_json_file_path = os.path.join(output_coco_json_dir, viaFolderName.split('.')[0] + '.json')
            path_images = os.path.join(root, imgs_Folder + '/' + viaFolderName.split('.')[0])
            print("开始转换第{}个VIA文件".format(num))
            via_to_coco(via_json_file,output_coco_json_file_path,path_images,csvTrans)
        print("VIA文件转换完成，输出路径为------>{}".format(os.path.join(root,out_Folder)))

    if json_file_combin is True:
        need_combin_Folder_Path = os.path.join(root,out_Folder)
        need_combin_FolderName = sorted(os.listdir(need_combin_Folder_Path))
        out_combin_Result_Path = os.path.join(root,combinResults)
        combin_coco_json_file(need_combin_FolderName,need_combin_Folder_Path,out_combin_Result_Path)
    print("COCO文件合并完成，输出路径为------>{}".format(root))

    if csvTrans is True:
        coco_json_path = os.path.join(root,combinResults + '/' + 'combinResults.json')
        out_csv_path = os.path.join(root,"csvResults")

        coco2csv(coco_json_path,out_csv_path)



