import os
from pycocotools.coco import COCO
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import math

# json_path = "/home/jzy/桌面/123.json"
json_path = "/home/jzy/MyMountDisk/jsonfile/3_nonabs_angle_center/json_file_hw_0-180/9.json"
# img_path = "/home/jzy/MyMountDisk/zylofor/location/dataset/annCat"
img_path = "/home/jzy/MyMountDisk/zylofor/AntennaDataSet/train/3/9"
# load coco data
coco = COCO(annotation_file=json_path)

# get all image index info
ids = list(sorted(coco.imgs.keys()))
print("number of images: {}".format(len(ids)))

# get all coco class labels
coco_classes = dict([(v["id"], v["name"]) for k, v in coco.cats.items()])

# 遍历前三张图像
for img_id in ids[:5]:
    # 获取对应图像id的所有annotations idx信息
    ann_ids = coco.getAnnIds(imgIds=img_id)

    # 根据annotations idx信息获取所有标注信息
    targets = coco.loadAnns(ann_ids)

    # get image file name
    path = coco.loadImgs(img_id)[0]['file_name']

    # read image
    img = Image.open(os.path.join(img_path, path)).convert('RGB')
    draw = ImageDraw.Draw(img)
    # draw box to image
    for target in targets:
        x, y, w, h,angle = target["bbox"]

        # x1, y1, x2, y2 = int(x-0.5*w), int(y-0.5*h), int(x+0.5*w), int(y+0.5*h)
        x33, y33, x22, y22, x11, y11, x00, y00 = int(x - 0.5 * w), int(y - 0.5 * h), int(x + 0.5 * w), int(
            y - 0.5 * h), int(x - 0.5 * w), int(y + 0.5 * h), int(x + 0.5 * w), int(y + 0.5 * h)

        anglePi = angle / 180 * math.pi
        anglePi = -anglePi if anglePi <= math.pi else anglePi - math.pi

        cosA = math.cos(anglePi)
        sinA = math.sin(anglePi)

        x0n = (x00 - x) * cosA - (y00 - y) * sinA + x
        y0n = (x00 - x) * sinA + (y00 - y) * cosA + y

        x1n = (x11 - x) * cosA - (y11 - y) * sinA + x
        y1n = (x11 - x) * sinA + (y11 - y) * cosA + y

        x2n = (x22 - x) * cosA - (y22 - y) * sinA + x
        y2n = (x22 - x) * sinA + (y22 - y) * cosA + y

        x3n = (x33 - x) * cosA - (y33 - y) * sinA + x
        y3n = (x33 - x) * sinA + (y33 - y) * cosA + y

        draw.line([(x0n, y0n), (x1n, y1n)], fill=(0, 0, 255), width=5)  # blue  横线
        draw.line([(x1n, y1n), (x3n, y3n)], fill=(255, 0, 0), width=5)  # red    竖线
        draw.line([(x3n, y3n), (x2n, y2n)], fill=(0, 0, 255), width=5)
        draw.line([(x0n, y0n), (x2n, y2n)], fill=(255, 0, 0), width=5)

        # draw.rectangle((x00, y00, x33, y33))
        draw.text((x22, y22), coco_classes[target["category_id"]],fill=(0,0,255),spacing=1000)



    # show image
    plt.axis('off')
    plt.imshow(img)
    plt.show()
