# =========================================================
# @date：   2021/9
# @version: v1.0
# @author： Jiang.Z.Y
# ==========================================================

import os
import random
import shutil
from shutil import copy2
import tqdm


def ShuffleRawDir(dataDir):
    splitTrainRate, splitValRate, splitTestRate = 0.7, 0.2, 0.1
    allData = os.listdir(dataDir)
    # print(allData)
    num_all_data = len(allData)
    print("num_all_data: " + str(num_all_data))
    index_list = list(range(num_all_data))
    # print(index_list)
    random.shuffle(index_list)
    trainSetIndex = index_list[:int(splitTrainRate * num_all_data)]
    valSetIndex = index_list[int(splitTrainRate * num_all_data):int(splitTrainRate * num_all_data)+int(splitValRate * num_all_data)]
    testSetIndex = index_list[int(splitTrainRate * num_all_data)+int(splitValRate * num_all_data):]
    return allData,num_all_data, trainSetIndex,valSetIndex,testSetIndex


def startSplit():
    print("---------------Start split train set !-------------------")
    for i in tqdm.tqdm(trainSetIndex):
        fileName = os.path.join(dataDir,allData[i])
        copy2(fileName,trainDir)

    print("---------------Start split valid set !-------------------")
    for j in tqdm.tqdm(valSetIndex):
        fileName = os.path.join(dataDir,allData[j])
        copy2(fileName,validDir)

    print("---------------Start split test set !--------------------")
    for k in tqdm.tqdm(testSetIndex):
        fileName = os.path.join(dataDir,allData[k])
        copy2(fileName,testDir)




def createDir():
    if not os.path.exists(trainDir):
        os.mkdir(trainDir)
    else:
        shutil.rmtree(trainDir)
        os.mkdir(trainDir)
    if not os.path.exists(validDir):
        os.mkdir(validDir)
    else:
        shutil.rmtree(validDir)
        os.mkdir(validDir)
    if not os.path.exists(testDir):
        os.mkdir(testDir)
    else:
        shutil.rmtree(testDir)
        os.mkdir(testDir)


if __name__ == '__main__':
    dataDir = "/home/jzy/MyMountDisk/zylofor/AntennaDataSet/train/3/10"  #（原始图片文件目录）
    trainDir = "/home/jzy/MyMountDisk/zylofor/dataSplit/train"  # （将训练集放在这个文件夹下）
    validDir = '/home/jzy/MyMountDisk/zylofor/dataSplit/val'  # （将验证集放在这个文件夹下）
    testDir = '/home/jzy/MyMountDisk/zylofor/dataSplit/test'  # （将测试集放在这个文件夹下）

    createDir()
    #打乱数据集
    allData,num_all_data, trainSetIndex,valSetIndex,testSetIndex = ShuffleRawDir(dataDir)
    startSplit()
    print("Split Done!\ntrainSaveDir:{}\nvalidSaveDir:{}\ntestSaveDir:{}".format(trainDir,validDir,testDir))
