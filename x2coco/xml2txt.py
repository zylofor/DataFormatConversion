from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree
import xml.dom.minidom
import os

saved_root = "/home/jzy/MyMountDisk/zylofor/location/dataset/new_complete2/2021_08_07_label/train_08_07.txt"

def wirteTxt(path,label,x1,y1,x2,y2,start=True):
    name = "train/"+path.split("\\")[-1].replace('xml','jpg')
    with open (saved_root,'a') as f:
        if start:
            f.write('\n')
            f.write("{} {},{},{},{},{}".format(name,x1,y1,x2,y2,label))
        else:
            f.write(" {},{},{},{},{}".format(x1, y1, x2, y2, label))

def readXML(path):
    domTree = parse(path)
    rootNode = domTree.documentElement
    # print(rootNode.nodeName)

    size = rootNode.getElementsByTagName("size")[0]
    width = int(size.getElementsByTagName("width")[0].childNodes[0].data)
    height = int(size.getElementsByTagName("height")[0].childNodes[0].data)

    # print(width)
    # print(height)

    objects = rootNode.getElementsByTagName("object")
    first_time = True
    for num, object in enumerate(objects):
        bndbox = object.getElementsByTagName("bndbox")[0]
        name = object.getElementsByTagName("name")[0].childNodes[0].data
        x1 = int(bndbox.getElementsByTagName("xmin")[0].childNodes[0].data)
        y1 = int(bndbox.getElementsByTagName("ymin")[0].childNodes[0].data)
        x2 = int(bndbox.getElementsByTagName("xmax")[0].childNodes[0].data)
        y2 = int(bndbox.getElementsByTagName("ymax")[0].childNodes[0].data)
        label = 0

        if label==1:
            continue

        if first_time:
            first_time=False
            wirteTxt(path,label,x1,y1,x2,y2,True)
        else:
            print(path)
            print(label)
            print(name)
            wirteTxt(path,label, x1, y1, x2, y2, False)

if __name__ == '__main__':
    root = "/home/jzy/MyMountDisk/zylofor/location/dataset/new_complete2/2021_08_07_label/trainLabel_08_07"
    for name in os.listdir(root):
        path = os.path.join(root,name)
        readXML(path)
    print("Done")