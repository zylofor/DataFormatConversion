import cv2
import tqdm
import os
import shutil

def mkdirPath():
    ##TODO:获取视频路径。
    videoName = "DJI_0006"
    videoPath = '/home/jzy/PaperLearning/MyUbuntu/Snake/data/video/{}'.format(videoName)
    if os.path.exists(videoPath):
        shutil.rmtree(videoPath)
    else:
        os.mkdir(videoPath)
    return videoName, videoPath

def video2image(rval,videoName):
    ##TODO:转换开始！
    print("Transfer starting!")
    n, i = 0, 0
    ##TODO：视频帧计数间隔频率
    timeF =1

    ##TODO：循环读取视频帧

    while rval:
        rval,frame = video.read()
        if (n % timeF == 0):
            i += 1
            print(i)
            cv2.imwrite('{}/{}.jpg'.format(videoName,i), frame)
        n += 1
    print("Done!")
    video.release()

if __name__ == '__main__':
    videoName, videoPath = mkdirPath()
    video = cv2.VideoCapture("/home/jzy/PaperLearning/MyUbuntu/Snake/data/video/{}.mp4".format(videoName))
    if video.isOpened():
        rval, frame = video.read()
        video2image(rval,videoPath)
    else:
        rval = False







