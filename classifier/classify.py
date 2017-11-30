from PIL import Image
from torch.autograd import Variable

import glob
import torch
import torchvision

import numpy as np
import torchvision.transforms as transforms
import torchvision.models as models

from torch.utils.data import Dataset, TensorDataset, DataLoader, ConcatDataset

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import scipy.misc
import timeit
import piexif

import math

start = timeit.default_timer()

"""
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 5 * 5, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
        self.fc4 = nn.Linear(10, 3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 16 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
"""

# 256x256 CNN
# CNN Model (2 conv layer)
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=5, padding=2),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(16, 32, kernel_size=5, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2))
        self.fc = nn.Linear(131072, 3)
        
    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.view(out.size(0), -1)
        out = self.fc(out)
        return out

net = Net()
net.load_state_dict(torch.load('Neural_Networks/Deep_CNN_17e.pth'))

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.001, momentum=0.9)

transform = transforms.Compose(
    [transforms.ToTensor(),
     transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

classes = ('Test')

# Iterate through Type 1 image files 
running_loss = 0.0

feature_list = []
target_list = []

image_folder = glob.iglob("../processed_images/Full_Size/Test/*.jpg")
image_folder = list(image_folder)

target_test = [2,2,1,3,3,2,2,2,2,2,2,3,2,3,2,3,1,2,2,3,1,2,2,1,2,1,2,3,2,3,1,2,2,1,2,3,2,2,2,1,3,2,2,2,1,3,1,1,3,3,3,1,3,1,3,3,2,2,2,1,3,2,3,2,2,1,3,3,3,3,1,2,2,1,3,1,3,2,3,1,2,2,2,3,1,2,3,3,2,3,1,2,3,2,2,2,1,3,2,3,1,2,2,1,2,2,2,2,3,3,2,1,3,3,2,2,2,2,3,2,2,2,3,1,3,2,2,2,2,2,2,3,3,3,2,2,2,2,2,2,2,3,1,3,2,3,2,2,2,3,1,3,2,3,1,3,2,3,3,2,1,2,2,2,2,1,1,3,1,2,2,3,2,1,2,3,2,2,3,2,3,1,3,2,3,3,2,2,2,3,2,2,3,1,2,1,1,2,3,3,2,2,2,2,2,3,2,3,3,3,3,2,2,3,2,2,2,2,2,2,2,3,3,3,3,2,2,2,2,2,2,1,1,2,3,2,2,2,3,2,3,2,2,2,3,2,2,2,1,1,2,1,3,3,3,2,3,2,3,3,1,3,2,2,1,3,3,2,1,2,3,2,3,3,2,3,2,2,3,3,2,2,2,3,3,2,2,3,3,1,2,2,2,1,3,2,2,2,3,1,2,3,2,1,1,2,3,3,1,3,3,3,1,2,2,2,1,1,2,2,2,2,2,3,2,3,3,2,3,3,1,1,2,3,3,3,1,2,2,3,2,2,1,3,1,1,2,2,2,2,2,2,2,3,2,1,1,2,2,3,2,2,2,2,3,2,3,1,2,2,2,1,3,3,2,2,3,1,2,3,3,2,1,2,2,2,3,3,2,2,2,2,2,3,2,1,2,2,2,2,3,3,1,2,2,2,1,2,2,3,3,2,3,2,3,1,1,2,3,1,2,2,3,3,2,3,3,2,3,3,1,1,3,3,2,3,2,2,2,2,3,2,2,2,2,1,2,2,2,1,3,2,3,1,2,3,2,1,1,2,1,2,2,3,2,2,2,1,2,3,2,2,1,2,2,2,2,1,2,3,3,3,1,2,3,3,2,2,2,1,2,3,2,1,2,2,3,2,2,3,2,2,3,2,3,2,2,2,2,2,2,3]

image_folder = sorted(image_folder, key = lambda x:int(x[int(len("../processed_images/Full_Size/Test/")):-8]))

for file_index, filename in enumerate(image_folder):
    piexif.remove(filename)
    image = Image.open(filename)
    try:
        image = scipy.misc.imresize(image, (256, 256))
    except ValueError:
        continue 
    image = np.array(image)
    image = np.swapaxes(image,0,2)
    feature_list.append(image)
    target_list.append(target_test[file_index])
    # print(image_folder[file_index])

feature_array = np.array(feature_list)
features = torch.from_numpy(feature_array)

# len(features)
correct = 0
total = 0 

outputs = np.zeros((len(features),3))

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

for i in range(0,len(features)):
    torch.manual_seed(i)
    output = net(Variable(features[i:i+1]).float())
    outputs[i] = (softmax(output.data.numpy())[0])

running_loss = 0
correct = 0
total = 0

for i in range(len(outputs)):
    if((outputs[i].argmax() + 1) != target_test[i]):
        # Add the log of the probability to the running loss
        running_loss += math.log1p(outputs[i][outputs[i].argmax()])
    else:
        correct += 1
    total += 1

print(running_loss/len(outputs))
print(correct/total)