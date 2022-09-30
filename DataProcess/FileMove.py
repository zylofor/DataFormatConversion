import os
import shutil
import numpy as np

def rename_file(src,target):
    os.rename(src,target)
    return target

def move_file(src,target):
    shutil.move(src,target)

def copy_file(src,target):
    shutil.copy(src,target)

def del_hidden_file(dir,file):
    for hidden_file in file:
        if hidden_file.split('_')[0] == '.'  :
            print(os.path.join(dir,hidden_file))
            os.remove(os.path.join(dir,hidden_file))


if __name__ == '__main__':
    src_root = "/home/lab315/jzy/PaperLearning/MyDatasets/zylofor/SteelDataset/2022-7-21-rev/已完成图像文件"
    target_root = "/home/lab315/jzy/PaperLearning/MyDatasets/zylofor/SteelDataset/2022-7-21-rev/output"
    arrFile = []
    num = 0
    np.random.seed(1)


    src_root_file = os.listdir(src_root)
    src_root_file.sort(key=lambda x:int(x.split('.')[0]))
    for Folder in src_root_file:
        dir = os.path.join(src_root,Folder)

        #Rename file!
        # rename_file(dir,os.path.join(src_root,str(num)))

        # Moving/Copy/DEL file!
        ori_file = os.listdir(dir)
        del_hidden_file(dir,ori_file)

        new_file = os.listdir(dir)
        new_file.sort(key=lambda x:int(x.split('.')[0]))


        for j in new_file:

            need_move_file_path = os.path.join(dir,j)
            # rename_after_file = rename_file(need_move_file_path,os.path.join(dir,str(num)+'.jpg'))

            print(need_move_file_path)
            copy_file(need_move_file_path,target_root)

            num = num+1




