from torchstat import stat
from dlanet_dcn_headDCN_augmentCNN import DlaNet
import torch
from torchvision import models



# x = torch.rand(1, 3, 512, 512)
model = DlaNet()
print(model)




#model = DlaNet(34)
# #print(model)
stat(model,(3,512,512))
